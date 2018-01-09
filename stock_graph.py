import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
#from matplotlib.ticker import EngFormatter
from matplotlib.finance import candlestick2_ohlc, volume_overlay
#from mpl_finance import candlestick2_ohlc, volume_overlay
from matplotlib.ticker import EngFormatter

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


stock_num = 7203
start = '2017-10-01'
# end   = '2017-12-01'  # End Date set
end = pd.to_datetime(pd.datetime.now())  # End Data is Today

stock_name = get_quote_yahoojp(stock_num, start=start, end=end)
# stock_name = stock_name[-30:]

# stock_name.plot(kind='ohlc')
# plt.grid(color='black', linestyle='-')
# plt.show()

# stock_name.asfreq('B').plot(kind='ohlc')
# plt.subplots_adjust(bottom=0.25)
# plt.grid(color='black', linestyle='-')
# plt.show()


# 2016年上半期の日経平均のデータを読み込む
start_date = "2017-10-01"
end_date = "2018-1-9"
df = pd.DataFrame(index=pd.date_range(start_date, end_date))
df = pd.DataFrame(index=pd.date_range(start, end))
df = df.join(stock_name)
df = df.dropna()
df.index.names = ['Date']

# ローソク足をプロット
fig = plt.figure(figsize=(8, 5))
#fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
candlestick2_ohlc(ax, df["Open"], df["High"], df["Low"], df["Adj Close"], width=0.9, colorup="b", colordown="r")
ax.set_xticklabels(df.index[::10].strftime("%Y-%m-%d"), rotation=90)  # 2017.12.31
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
plt.show()

""" Plot Adj Close Graph"""
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

stock_list.plot(y=['Adj Close'])
#stock_list['Adj Close'].plot(legend=True, figsize=(8,5))
stock_list['Adj Close'].plot(legend=True)

stock_list['MA5'].plot(legend=True)
stock_list['MA25'].plot(legend=True)
plt.grid(color='y', linestyle='-')
plt.show()