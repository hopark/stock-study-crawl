import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings
from bs4 import BeautifulSoup as bs
import pandas as pd

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36", "x-Requested-With": "XMLHttpRequest"}
warnings.simplefilter('ignore',InsecureRequestWarning)
stock_list = []
with requests.Session() as s:
    def getHTML(url):
        page = s.get(url, headers=headers, verify=False, timeout=30)
        html = page.text
        return bs(html, 'html.parser')
    korea_page = getHTML('https://kr.investing.com/equities/StocksFilter?noconstruct=1&smlID=694&sid=&tabletype=price&index_id=all')
    stockHtml = korea_page.select('td.plusIconTd > a')
    for stock in stockHtml:
        stock_info = {}
        stock_info['이름'] = stock['title']
        print(stock['title'])
        stock_info['링크'] = stock['href']
        stock_page = getHTML('https://kr.investing.com' + stock['href'])
        information = stock_page.select('div.overviewDataTable > div.inlineblock')
        for info in information:
            field = info.select_one('span.float_lang_base_1').text
            data = info.select_one('span.float_lang_base_2').text
            stock_info[field] = data
        stock_list.append(stock_info)
    data = pd.DataFrame(stock_list, columns=stock_list[0].keys())
    data.to_csv('result.csv', encoding='utf-8', sep=',')