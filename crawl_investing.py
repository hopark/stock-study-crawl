import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings
import pandas as pd
import json
import sys

import syspath
from crawl.modules import MySession as Session, constant as CONST, util

warnings.simplefilter('ignore', InsecureRequestWarning)


def extractBalanceInfo(cell):
    data = cell.select('td')
    field = data[0].text
    amount = "" if data[1].text == "" or data[1].text == "-" else float(
        data[1].text)
    return field, amount


def getStockInfoByPage(session, page_num, crawl_num):
    stock_info = session.post(CONST.SEARCH_URL, data={
        **CONST.KOR_STOCK_PARAM, "pn": str(page_num+1)}).json()['hits'][:crawl_num]
    stock_id_list = [stock_info[i]['pair_ID']
                     for i in range(len(stock_info))]
    crawled_num = len(stock_info)
    return stock_info, stock_id_list, crawled_num


def getBalanceInfoByPage(session, stock_id_list):
    balance_info = list()
    for stock_id in stock_id_list:
        balance_sheet = util.getBalanceSheetHTML(session, stock_id)
        balance_cells = balance_sheet.select('tr.pointer')
        balance_dict = dict()
        for cell in balance_cells:
            field, amount = extractBalanceInfo(cell)
            balance_dict[field] = amount
        balance_info.append(balance_dict)
    return balance_info


def getAverageProfitByPage(session, stock_id_list):
    profit_info = list()
    for stock_id in stock_id_list:
        profit_sheet = util.getProfitHTML(session, stock_id)
        total = 0
        num = 0
        profit_cells = profit_sheet.select(
            'table.genTbl.openTbl.companyFinancialSummaryTbl > tbody > tr')[2]
        profit_data = [cell.text for cell in profit_cells.select('tr')[1:]]
        for data in profit_data:
            if data == '' or data == '-':
                break
            total += int(data)
            num += 1
        if num == 0:
            avg = 0
        else:
            avg = total/num
        profit_info.append({'avg_profit': avg})
        return profit_info


def crawlStockInfo():
    with Session.MySession() as session:
        session.setOptions(headers=CONST.SEARCH_HEADER,
                           timeout=30, verify=False, proxies=util.getProxy())
        total_stock_info = list()
        total_crawled_num = 0
        total_stock_num = util.getTotalStockNum()
        if total_stock_num == CONST.GET_ALL_STOCK:
            total_stock_num = util.getAllStockNum(session)
        total_page_num = int((total_stock_num-1)/CONST.STOCK_PER_PAGE)+1
        for page_num in range(total_page_num):
            remain_crawl_num = total_stock_num - total_crawled_num
            crawl_num = CONST.STOCK_PER_PAGE if remain_crawl_num > CONST.STOCK_PER_PAGE else remain_crawl_num
            stock_info, stock_id_list, crawled_num = getStockInfoByPage(
                session, page_num, crawl_num)
            balance_info = getBalanceInfoByPage(session, stock_id_list)
            profit_info = getAverageProfitByPage(session, stock_id_list)
            total_stock_info += [{**stock, **balance, **profit}
                                 for stock, balance, profit in zip(stock_info, balance_info, profit_info)]
            total_crawled_num += crawled_num
            progress = total_crawled_num/total_stock_num*100
            print(
                f'Progress: {total_crawled_num}/{total_stock_num} ({progress:.2f}%)')
    return total_stock_info


def preprocessData(data):
    columns = data.columns.to_list()
    drop_columns = util.getDropColumns(columns)
    data.drop(columns=drop_columns, axis=1, inplace=True)
    rename_columns = {'총유동자산': 'current_assets', '총 자산': 'assets',
                      '총유동부채': 'current_liabilities', '총부채': 'liabilities', '총자본': 'capital'}
    data.rename(columns=rename_columns, inplace=True)
    return data


def main():
    util.setParser()
    total_stock_info = crawlStockInfo()
    stock_data = pd.DataFrame(total_stock_info)
    stock_data = preprocessData(stock_data)
    stock_data.to_csv(CONST.OUTPUT_CSV, encoding='utf-8', sep=',', index=False)


if __name__ == '__main__':
    main()
