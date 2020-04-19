import requests
import re
import sys
import json
from pandas import json_normalize
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import argparse

from modules.constant import CONST

_All_STOCK_LIST = None
_STOCK_LIST = None
_PROXY = None
_ENCPARAM = None

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

def setAllStockList():
    global _All_STOCK_LIST
    html = bs(GETtoLimit(CONST.Url.STOCK_LIST).text, 'html.parser')
    stock_list = html.select('form#chkFrm > div > select > option')
    all_stock_list = [(stock['value'], stock.text.replace(' ', '')) for stock in stock_list]
    _All_STOCK_LIST = all_stock_list

def getAllStockList():
    global _All_STOCK_LIST
    return _All_STOCK_LIST

def GETtoLimit(url, limit=None, headers={}):
    tries = 0
    while limit == None or tries < limit:
        try:
            return requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            tries += 1
            print(f'retry GET {tries} time(s).')
            time.sleep(1)
    raise ConnectionError

def getStockByCode(stock_code):
    global _All_STOCK_LIST
    for code, name in _All_STOCK_LIST:
        if code.lower() == stock_code.lower():
            return (code, name)
    raise ValueError('Wrong stock code.')

def getStockByName(stock_name):
    global _All_STOCK_LIST
    for code, name in _All_STOCK_LIST:
        if name.lower() == stock_name.lower():
            return (code, name)
    raise ValueError('Wrong stock name.')

def setStockListAsAll():
    global _STOCK_LIST, _All_STOCK_LIST
    _STOCK_LIST = _All_STOCK_LIST

def setStockListByCode(stock_code):
    global _STOCK_LIST
    stock = getStockByCode(stock_code)
    _STOCK_LIST = [stock]

def setStockListByName(stock_name):
    global _STOCK_LIST
    stock = getStockByCode(stock_name)
    _STOCK_LIST = [stock]

def setParser():
    parser = argparse.ArgumentParser(description='Crawl stock_info')
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument(
        '-a', '--all', help='All of stocks', action='store_true')
    parser_group.add_argument(
        '-c', '--code', help='code of stock', type=str.lower)
    parser_group.add_argument(
        '-n', '--name', help='name of stock', type=str.lower)
    parser.add_argument('-p', '--place', help='Place to set proxy from company',
                        default='', type=str, choices=['suwon', 'seoul'])

    args = parser.parse_args()
    if args.all == True:
        setStockListAsAll()
    elif args.code != None:
        setStockListByCode(args.code)
    elif args.name != None:
        setStockListByName(args.name)
    else:
        raise Exception('No stock from conditions.')
    setProxy(args.place)

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
        html_text = GETtoLimit(url, headers=headers).text
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
    data = json.loads(GETtoLimit(url, headers=headers).text.replace('\\r', ' '))
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


    if _STOCK_LIST == None:
        print('No stock from conditions.')
        exit(1)
    setProxy(args.place)

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
        html_text = GETtoLimit(url, headers=headers).text
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
    data = json.loads(GETtoLimit(url, headers=headers).text.replace('\\r', ' '))
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
