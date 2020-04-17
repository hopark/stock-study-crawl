# stock-study-crawl

[![codecov](https://codecov.io/gh/hopark/stock-study-crawl/branch/feat/pytest/graph/badge.svg)](https://codecov.io/gh/hopark/stock-study-crawl)

## File tree

```
.
|-- modules
|   `-- __init__.py
|   `-- constant.py
|   `-- util.py
|-- crawl_investing.py
|-- README.md
|-- requirements.txt
`-- stock_info.csv
```

## Install modules

> $ pip install -r requirements.txt 

## Crawl investing

**exec**

> $ python crawl_investing.py `(-a | -c CODE | -n NAME)` `[-p {suwon,seoul}]`

**example**

- _Crawl all stocks in korea_

> $ python crawl_investing --all

- _Crawl a specific stock with stock code_

> $ python crawl_investing --code 039489

- _Crawl a specific stock with stock name_

> $ python crawl_investing --name 가우스전자

- _Crawl stock information via proxy (in company)_

> $ python crawl_investing --all --proxy suwon*

**help**

> $ python crawl_investing --help


## Results

- output : `stock_info.csv`

- field : infomation of all stocks in korea & balance sheet data in last year
