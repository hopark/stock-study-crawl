import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse
import warnings
import pandas as pd
import json
import sys

from modules import util
from modules.constant import CONST

warnings.simplefilter('ignore', InsecureRequestWarning)

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
        util.setStockList(CONST.StockType.ALL_STOCK)
    elif args.code != None:
        util.setStockList(CONST.StockType.CODE, args.code)
    elif args.name != None:
        util.setStockList(CONST.StockType.NAME, args.name)
    
    if util.getStockList() == None:
        print('No stock from conditions.')
        exit(1)
    util.setProxy(args.place)
    

def main():
    setParser()
    stock_list = util.getExpectedValues()
    stock_data = pd.DataFrame(stock_list).set_index('code')
    stock_data.to_csv('stock_info.csv', encoding='euc-kr')

if __name__ == '__main__':
    main()
