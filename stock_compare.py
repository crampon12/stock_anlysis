import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import seaborn as sns

# financeはmatplotlib 2.2で削除予定、以後はmpl_financeを有効にすること
from matplotlib.finance import candlestick2_ohlc, volume_overlay

def get_quote_yahoojp(code, start=None, end=None, interval='d'):
    base = 'https://info.finance.yahoo.co.jp/history/?code={0}.T&{1}&{2}&tm={3}&p={4}'
    # start, end = web._sanitize_dates(start, end)
    start = pd.to_datetime(start)
    if end == None:
        end = pd.to_datetime(pd.datetime.now())
    else:
        end = pd.to_datetime(end)
    start = 'sy={0}&sm={1}&sd={2}'.format(start.year, start.month, start.day)
    end = 'ey={0}&em={1}&ed={2}'.format(end.year, end.month, end.day)
    p = 1
    results = []

    if interval not in ['d', 'w', 'm', 'v']:
        raise ValueError("Invalid interval: valid values are 'd', 'w', 'm' and 'v'")

    while True:
        url = base.format(code, start, end, interval, p)
        tables = pd.read_html(url, header=0)
        if len(tables) < 2 or len(tables[1]) == 0:
            break
        results.append(tables[1])
        p += 1
    result = pd.concat(results, ignore_index=True)

    result.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
    if interval == 'm':
        result['Date'] = pd.to_datetime(result['Date'], format='%Y年%m月')
    else:
        result['Date'] = pd.to_datetime(result['Date'], format='%Y年%m月%d日')
    result = result.set_index('Date')
    result = result.sort_index()
    return result


#目的となる銘柄コードの指定
stock_num = ['4579', '3825', '7575', '6775']
# 開始年月日を指定
start_date = "2017-10-01"
# 終了日時を指定、日時指定または現在日時
#end_date = "2018-1-9"
end_date = pd.to_datetime(pd.datetime.now())  # End Data is Today

#バッファ用DataFrameの作成
df = DataFrame()
for i in range(len(stock_num)):
    # yahooからデータを取得する関数を呼び出し
    stock_name = get_quote_yahoojp(stock_num[i], start=start_date, end=end_date)
    stock_name = stock_name.rename(columns={'Adj Close':stock_num[i]}) # 列の名前変更
    stock_name = stock_name.drop('Open',axis=1) # 列の削除
    stock_name = stock_name.drop('High',axis=1)
    stock_name = stock_name.drop('Low',axis=1)
    stock_name = stock_name.drop('Close',axis=1)
    stock_name = stock_name.drop('Volume',axis=1)
    if i == 0:
        df = stock_name
    else:
        #pd.merge(df,stock_name,left_index=True)
        df = pd.concat([df, stock_name], axis=1)

sns.set_style('whitegrid')
# 別のDataFrameにしておきます。
tech_rets = df.pct_change()
#sns.jointplot('4579','3825',tech_rets,kind='scatter',color='seagreen')

# ヒートマップ描画
sns.heatmap(tech_rets.corr(), annot=True)

# データを格納しているDataFrameを引数にして、PairGridを作ります。
returns_fig = sns.PairGrid(tech_rets.dropna())

# 右上側に描くグラフの種類を指定します。
returns_fig.map_upper(plt.scatter,color='purple')

# 同じように、左下側には、KDEプロットを描くことにしましょう。
returns_fig.map_lower(sns.kdeplot,cmap='cool_d')

# 対角線上には、ヒストグラムを描くことにします。
returns_fig.map_diag(plt.hist,bins=30)

plt.show()

