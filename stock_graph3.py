import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt

# financeはmatplotlib 2.2で削除予定、以後はmpl_financeを有効にすること
from matplotlib.finance import candlestick2_ohlc, volume_overlay
#from mpl_finance import candlestick2_ohlc, volume_overlay
from matplotlib.ticker import EngFormatter
from matplotlib.widgets import Cursor

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

# 銘柄番号を指定すること
stock_num = 7203
# 開始年月日を指定
start = '2017-10-01'
# 終了日時を指定、日時指定または現在日時
# end   = '2017-12-01'  # End Date set
end = pd.to_datetime(pd.datetime.now())  # End Data is Today

# yahooからデータを取得する関数を呼び出し
stock_name = get_quote_yahoojp(stock_num, start=start, end=end)

# 2016年上半期の日経平均のデータを読み込む
start_date = "2017-10-01"
end_date = "2018-1-9"
df = pd.DataFrame(index=pd.date_range(start_date, end_date))
#df = pd.DataFrame(index=pd.date_range(start, end))
df = df.join(stock_name)
df = df.dropna()
df.index.names = ['Date']

# ローソク足をプロット
fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(2, 1, 1) # 描画領域2行1列の1行目に描画する
candlestick2_ohlc(ax, df["Open"], df["High"], df["Low"], df["Adj Close"], width=0.9, colorup="b", colordown="r")
ax.set_xticklabels(df.index[::10].strftime("%m-%d"), rotation=45)  # 2017.12.31
ax.set_xlim([0, df.shape[0]])  # 横軸の範囲はデータの個数(df.shape[0]個)までに変更しておく
ax.set_ylabel("Price")

plt.grid(color='y', linestyle='-')

# ローソク足を上側75%に収める
bottom, top = ax.get_ylim()
ax.set_ylim(bottom - (top - bottom) / 4, top)

# 出来高のチャートをプロット
ax2 = ax.twinx()
volume_overlay(ax2, df["Open"], df["Adj Close"], df["Volume"], width=1, colorup="g", colordown="g")
ax2.set_xlim([0, df.shape[0]])

# 出来高チャートは下側25%に収める
ax2.set_ylim([0, df["Volume"].max() * 4])
ax2.set_ylabel("Volume")
formatter = EngFormatter()
ax2.yaxis.set_major_formatter(formatter)
#plt.show()

""" Plot Adj Close Graph  終値のグラフ描画処理"""
# 5days, 25days移動平均の計算
MA5=stock_name['Adj Close'].rolling(window=5).mean()
MA25=stock_name['Adj Close'].rolling(window=25).mean()

# from Series to Dataframe
ma5_df=DataFrame(MA5)
ma25_df=DataFrame(MA25)

# Rename Columns
ma5_df = ma5_df.rename(columns={'Adj Close':'MA5'})
ma25_df = ma25_df.rename(columns={'Adj Close':'MA25'})
# Marge to "stock_name" and "ma5_df"
stock_list=stock_name.join(ma5_df)
# Marge to "stock_name" and "ma25_df"
stock_list=stock_list.join(ma25_df)

# 上のローソク足グラフとDataFrameの同じ画面での描画が上手くできなかったので
# 行列に変換してから描画する。
array = stock_list.as_matrix()
array = array.T # 転置行列
#print(array[5]) # for debug

ax3 = fig.add_subplot(2,1,2) # 2行目に描画する
ax3.set_xticklabels(stock_list.index[::10].strftime("%Y-%m-%d"), rotation=45)  # 2017.12.31
ax3.plot(array[5], label='Adj Close')
ax3.plot(array[6], label='MA5')
ax3.plot(array[7], label='MA25')
ax3.legend(loc=2)

ax3.set_xlim([0, stock_list.shape[0]])  # 横軸の範囲はデータの個数(df.shape[0]個)までに変更しておく
ax3.set_ylabel("Price")
cursor = Cursor(ax3, useblit=True, color='red', linewidth=1)
plt.grid(color='y', linestyle='-')
plt.show()