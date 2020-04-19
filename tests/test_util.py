from ..modules import util
from ..modules.constant import CONST

def testProxy():
    util.setProxy('seoul')
    assert util.getProxy() == {
        'http': f'http://{CONST.IP.SEOUL}/',
        'https': f'http://{CONST.IP.SEOUL}/',
        'ftp': f'ftp://{CONST.IP.SEOUL}/'
        }

    util.setProxy('suwon')
    assert util.getProxy() == {
        'http': f'http://{CONST.IP.SUWON}/',
        'https': f'http://{CONST.IP.SUWON}/',
        'ftp': f'ftp://{CONST.IP.SUWON}/'
    }

    util.setProxy('gumi')
    assert util.getProxy() == {}

    util.setProxy('')
    assert util.getProxy() == {}