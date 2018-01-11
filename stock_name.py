"""
### 銘柄コードから銘柄名(社名)を取得する関数 ###
### MatplotlibやSeabornが日本語対応になった時に使う予定 ###
参照元
武器商人＠Pythonのブログ PythonでYahoo!ファイナンスから株価を取得
http://oneshotlife-python.hatenablog.com/entry/Python%E3%81%A7Yahoo%E3%83%95%E3%82%A1%E3%82%A4%E3%83%8A%E3%83%B3%E3%82%B9%E3%81%8B%E3%82%89%E6%A0%AA%E4%BE%A1%E3%82%92%E5%8F%96%E5%BE%97 """

import requests
from bs4 import BeautifulSoup

def get_stockprice(code):
    base_url = "http://stocks.finance.yahoo.co.jp/stocks/detail/"
    query = {}
    query["code"] = code + ".T"
    ret = requests.get(base_url,params=query)
    soup = BeautifulSoup(ret.content,"lxml")
    stocktable =  soup.find('table', {'class':'stocksTable'})
    symbol =  stocktable.findAll('th', {'class':'symbol'})[0].text
    stockprice = stocktable.findAll('td', {'class':'stoksPrice'})[1].text
    return symbol,stockprice
if __name__ == "__main__":
    symbol,stockprice = get_stockprice("4579")
    print (symbol)
    print (stockprice)
    print (symbol,stockprice)
