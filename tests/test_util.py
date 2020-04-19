import pytest
import requests

from modules.util import *
from modules.constant import CONST

def testProxy():
    assert getProxy() == None

    setProxy('seoul')
    assert getProxy() == {
        'http': f'http://{CONST.IP.SEOUL}/',
        'https': f'http://{CONST.IP.SEOUL}/',
        'ftp': f'ftp://{CONST.IP.SEOUL}/'
        }

    setProxy('suwon')
    assert getProxy() == {
        'http': f'http://{CONST.IP.SUWON}/',
        'https': f'http://{CONST.IP.SUWON}/',
        'ftp': f'ftp://{CONST.IP.SUWON}/'
    }

    setProxy('gumi')
    assert getProxy() == {}

    setProxy('')
    assert getProxy() == {}

def testAllStockList():
    assert getAllStockList() == None

    setAllStockList()
    assert getAllStockList() != None

def testGETtoLimit():
    assert GETtoLimit('http://www.navar.com', 1).status_code == 200
    assert GETtoLimit(CONST.Url.STOCK_INFO.format(stock_code='000000'), 1).status_code == 200

    with pytest.raises(requests.exceptions.MissingSchema):
        GETtoLimit('', 1)  

    with pytest.raises(ConnectionError):
        GETtoLimit('http://localhost', 1)

def testGetStock():
    assert getStockByCode('005930') == ('005930', '삼성전자')
    assert getStockByName('삼성전자') == ('005930', '삼성전자')

    with pytest.raises(ValueError):
        getStockByCode('000000')

    with pytest.raises(ValueError):
        getStockByName('가우스전자')