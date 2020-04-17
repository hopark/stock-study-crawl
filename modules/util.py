import requests
import re
import sys
import json
from pandas import json_normalize
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

from .constant import CONST

_STOCK_LIST = None
_PROXY = None
_ENCPARAM = None

def GET(url, headers={}):
    tries = 0
    while True:
        try:
            return requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            tries += 1
            print(f'retry GET {tries} time(s).')
            time.sleep(1)


def getAllStockList():
    html = bs(GET(CONST.Url.STOCK_LIST).text, 'html.parser')
    stock_list = html.select('form#chkFrm > div > select > option')
    stock_list = [(stock['value'], stock.text.replace(' ', '')) for stock in stock_list]
    return stock_list

def setStockList(stock_type, val=None):
    global _STOCK_LIST
    stock_list = getAllStockList()
    if stock_type == CONST.StockType.ALL_STOCK:
        _STOCK_LIST = stock_list
    elif stock_type == CONST.StockType.CODE:
        for code, name in stock_list:
            if code.lower() == val:
                _STOCK_LIST = [(code, name)]
    elif stock_type == CONST.StockType.NAME:
        for code, name in stock_list:
            if name.lower() == val:
                _STOCK_LIST = [(code, name)]

def getStockList():
    global _STOCK_LIST
    return _STOCK_LIST

def setProxy(place):
    global _PROXY
    if place == 'suwon':
        ip = CONST.IP.SUWON
    elif place == 'seoul':
        ip = CONST.IP.SEOUL
    else:
        _PROXY = {}
        return

    _PROXY = {
        'http': f'http://{ip}/',
        'https': f'http://{ip}/',
        'ftp': f'ftp://{ip}/'
    }


def getProxy():
    global _PROXY
    return _PROXY

def convertType(num):
    try:
        tmp = float(num)
        if int(tmp) == tmp:
            return int(tmp)
        else:
            return tmp
    except ValueError:
        return num

def getStockInfo(stock_code):
    try:
        global _ENCPARAM
        url = CONST.Url.STOCK_INFO.format(stock_code=stock_code)
        headers={'Referer': url}
        html_text = GET(url, headers=headers).text
        _ENCPARAM = re.findall("encparam: '(.*?)'", html_text)[0]
        info_table = bs(html_text, 'html.parser').select('table#cTB11 > tbody > tr')
        stock_price = None
        issued_num = None
        for row in info_table:
            if row.select_one('th.txt') != None:
                if '주가' in row.select_one('th.txt').text:
                    stock_price = int(row.select_one('td.num > strong').text.replace(',', ''))
                elif '발행주식수' in row.select_one('th.txt').text:
                    issued_num = int(re.findall('([0-9,]*?)주', row.select_one('td.num').text)[0].replace(',', ''))
        index_field = ['EPS', 'BPS', 'PER', 'industry_PER', 'PBR', 'dividend_yield']
        index_val = [val.text.replace(',', '').replace('N/A', '') for val in bs(html_text, 'html.parser').select('td.cmp-table-cell.td0301 > dl > dt > b.num')]
        index = {field: convertType(val) for field, val in zip(index_field, index_val)}
    except:
        raise Exception('정상주식 정보가 아닙니다.')
    
    return stock_price, issued_num, index


def getStockSheet(stock_code, info_type):
    # info_type: profit(0), balance(1)
    global _ENCPARAM
    url = CONST.Url.STOCK_SHEET.format(stock_code=stock_code, rpt=info_type.value, encparam=_ENCPARAM)
    headers={'Referer': url}
    data = json.loads(GET(url, headers=headers).text.replace('\\r', ' '))
    try:
        data = json_normalize(data, 'DATA').sort_values(by=['ACC_NM'])
        data['ACC_NM'] = data['ACC_NM'].str.replace('.', '')
        data = data.drop_duplicates(subset='ACC_NM', keep='last').set_index('ACC_NM')
    except KeyError:
        return pd.DataFrame()
    return data

def calcExpectedValue(profit_data, bal_data, issued_num):
    try:
        profit_list = [
            profit_data[CONST.Year.LAST]['영업이익'] or 0,
            profit_data[CONST.Year.THIS]['영업이익'] or 0,
            profit_data[CONST.Year.NEXT]['영업이익'] or 0
        ]
        profit_num = sum(0 if profit == 0 else 1 for profit in profit_list)
        avg_profit = sum(profit_list)/profit_num
        business_value = avg_profit*CONST.Num.VALUE_CONST
        recent_balance = bal_data[CONST.Year.THIS]
        property_value = recent_balance['유동자산'] - (recent_balance['유동부채']*1.2) + recent_balance['투자자산']
        liabilities = recent_balance['비유동부채']

        coperate_value = business_value + property_value - liabilities
        coperate_value *= 100000000
        stock_value = coperate_value/issued_num
        return int(stock_value)
    except (KeyError, ValueError):
        return 'N/A'

def getExpectedValueByStock(stock_code, issued_num):
    profit_data = getStockSheet(stock_code, CONST.InfoType.PROFIT).fillna(0)
    bal_data = getStockSheet(stock_code, CONST.InfoType.BALANCE).fillna(0)
    if profit_data.empty or bal_data.empty:
        raise Exception('기업 분석 정보가 없습니다.')
    expected_value = calcExpectedValue(profit_data, bal_data, issued_num)

    return expected_value

def getExpectedValues():
    stock_list = []
    count = 0
    passed = 0
    for code, name in _STOCK_LIST:
        count += 1
        count_str = f'{code}: {name} ({count}/{len(_STOCK_LIST)})'
        try:
            stock_price, issued_num, index = getStockInfo(code)
            expected_value = getExpectedValueByStock(code, issued_num)
        except Exception as e:
            print(f'{count_str} Skip. - {e}')
            continue
        stock_list.append({
            'code': code,
            'name': name,
            'stock_price': stock_price,
            'expectd_value': expected_value,
            **index
        })
        passed += 1
        print(count_str + " Pass.")
    print(f'{passed}/{len(_STOCK_LIST)} stock(s) passed.')
    return stock_list
