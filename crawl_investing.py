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

def init():
    try:
        util.setParser()
        util.setAllStockList()
    except Exception as e:
        print(e)
        raise Exception

def main():
    try:
        init()
        stock_list = util.getExpectedValues()
        stock_data = pd.DataFrame(stock_list).set_index('code')
        stock_data.to_csv('stock_info.csv', encoding='euc-kr')
    except Exception:
        exit(1)

if __name__ == '__main__':
    main()
