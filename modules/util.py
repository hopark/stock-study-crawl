import argparse
from bs4 import BeautifulSoup as bs

import crawl.modules.constant as CONST

_TOTAL_STOCK_NUM = 0
_PROXY = {}


def setTotalStockNum(total_stock_num):
    global _TOTAL_STOCK_NUM
    _TOTAL_STOCK_NUM = total_stock_num


def getTotalStockNum():
    global _TOTAL_STOCK_NUM
    return _TOTAL_STOCK_NUM


def getAllStockNum(session):
    global _TOTAL_STOCK_NUM
    total_count = session.post(CONST.SEARCH_URL, data=CONST.KOR_STOCK_PARAM).json()[
        'totalCount']
    setTotalStockNum(total_count)
    return getTotalStockNum()


def setProxy(place):
    global _PROXY
    if place == 'suwon':
        ip = CONST.SUWON_IP
    elif place == 'seoul':
        ip = CONST.SEOUL_IP
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


def setParser():
    parser = argparse.ArgumentParser(description='Crawl kr.investing.com.')
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument(
        '-t', '--total', help='Number of stocks', default=-1, type=int)
    parser_group.add_argument(
        '-a', '--all', help='All of stocks', action='store_true')
    parser.add_argument('-p', '--place', help='Place to set proxy from company',
                        default='', type=str, choices=['suwon', 'seoul'])

    args = parser.parse_args()
    setTotalStockNum(args.total)
    setProxy(args.place)


def UrlToHTML(session, url):
    page = session.get(url)
    html = page.text
    return bs(html, 'html.parser')


def getBalanceSheetHTML(session, stock_id):
    bal_url = CONST.BALANCE_SHEET_URL.format(stock_id=stock_id)
    html = UrlToHTML(session, bal_url)
    return html


def getProfitHTML(session, stock_id):
    profit_url = CONST.PROFIT_URL.format(stock_id=stock_id)
    html = UrlToHTML(session, profit_url)
    return html


def areDigit(arr):
    for val in arr:
        if val == '' or val == '-':
            return False
    return True


def getExpectedPrice(stock_info):
    price = stock_info['avg_profit']*10
    if price == 0:
        return '-'
    if areDigit([stock_info['총 자산'], stock_info['총유동부채'], stock_info['총부채'], stock_info['sharesout']]):
        price += stock_info['총 자산'] - (stock_info['총유동부채']*1.2)
        price -= stock_info['총부채'] - stock_info['총유동부채']
        price /= int(stock_info['sharesout'])
        return price
    return '-'


def getDropColumns(columns):
    return [l for l in columns for end in ['_us', '_eu', '_frmt'] if l.endswith(end)]
