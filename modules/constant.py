# IP
SUWON_IP = '168.219.61.252:8080'
SEOUL_IP = '10.112.1.184:8080'

# CRAWL
SEARCH_VIEW_URL = 'https://kr.investing.com/stock-screener'
SEARCH_URL = 'https://kr.investing.com/stock-screener/Service/SearchStocks'
BALANCE_SHEET_URL = 'https://kr.investing.com/instruments/Financials/changereporttypeajax?action=change_report_type&pair_ID={stock_id}&report_type=BAL&period_type=Annual'
SEARCH_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
                 "x-Requested-With": "XMLHttpRequest"}
KOR_STOCK_PARAM = {"country[]": "11",
                   "sector": "3,1,7,6,12,2,8,9,10,11,5,4",
                   "industry": "18,53,67,89,43,31,6,38,87,77,66,81,48,16,11,54,33,24,20,29,91,36,73,21,50,3,63,7,10,86,78,101,27,90,85,82,2,96,8,22,14,45,92,65,40,70,42,39,99,98,79,64,80,15,26,44,74,97,76,88,17,12,47,62,68,83,84,57,35,72,51,25,28,5,60,19,4,61,37,34,93,71,30,102,100,58,95,94,32,13,46,1,52,23,75,56,59,41,49,55,69,9",
                   "equityType": "ORD,DRC,Preferred,Unit,ClosedEnd,REIT,ELKS,OpenEnd,Right,ParticipationShare,CapitalSecurity,PerpetualCapitalSecurity,GuaranteeCertificate,IGC,Warrant,SeniorNote,Debenture,ETF,ADR,ETC,ETN",
                   "exchange[]": ["130", "110", "60"],
                   "order[col]": "eq_market_cap",
                   "order[dir]": "d"}
STOCK_PER_PAGE = 50
GET_ALL_STOCK = -1

OUTPUT_CSV = 'stock_info.csv'
