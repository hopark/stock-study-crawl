from enum import Enum

class CONST:
    class IP:
        SUWON = '168.219.61.252:8080'
        SEOUL = '10.112.1.184:8080'
    class Url:
        STOCK_LIST = 'https://www.ktb.co.kr/trading/popup/itemPop.jspx'
        STOCK_INFO = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={stock_code}&cn='
        STOCK_SHEET = 'https://navercomp.wisereport.co.kr/v2/company/cF3002.aspx?cmp_cd={stock_code}&frq=0&rpt={rpt}&frqTyp=0&finGubun=MAIN&cn=&encparam={encparam}'
        SUMMARY = 'https://navercomp.wisereport.co.kr/v2/company/cF1001.aspx?cmp_cd={stock_code}&fin_typ=0&freq_typ=A&encparam={encparam}'
    class InfoType(Enum):
        PROFIT = 0
        BALANCE = 1
    class StockType(Enum):
        ALL_STOCK = 0
        CODE = 1
        NAME = 2
    class Year:
        LAST = 'DATA4'
        THIS = 'DATA5'
        NEXT = 'DATA6'
    class Num:
        VALUE_CONST = 9.09
