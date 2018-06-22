import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib
import ccxt
from datetime import datetime

Lot = 1


# region ### Methods

def convert_timeframe(quotes, rule='60Min'):
    quotes['timestamp'] = [datetime.utcfromtimestamp(item / 1000) for item in quotes['timestamp']]
    quotes.set_index('timestamp', inplace=True)
    # define how the df is re-sampled
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
    }

    # resample the df
    return quotes.resample(rule=rule, closed='left', label='left').apply(ohlc_dict)


def show_results(show_chart=True):
    df = pd.read_csv('totalReport.csv', ';', skiprows=1,
                     names=['symbol', 'index', 'dateOpen', 'priceOpen', 'dateClose', 'priceClose', 'profit'])

    list_balance = []
    balance = 0
    for x in df['profit']:
        balance += x
        list_balance.append(balance)
    max_element = list_balance[0]
    loss = []
    for items in list_balance:
        if items > max_element:
            max_element = items
        loss.append(max_element - items)

    max_loss = max(loss)
    balance = list_balance[-1]
    if max_loss == 0:
        max_loss = 1
    recovery_factor = round(balance / max_loss, 2)

    # z-score
    df_profit = df['profit']
    prev_trade = None
    pos_series = 0
    neg_series = 0
    for trade in df_profit:
        if prev_trade is None:
            prev_trade = float(trade)
            continue

        if float(trade) < 0 < prev_trade:
            pos_series += 1
        elif float(trade) > 0 > prev_trade:
            neg_series += 1

        prev_trade = float(trade)

    total_negative_trades = float(df[df['profit'] < 0].count()[0])
    total_positive_trades = float(df[df['profit'] > 0].count()[0])
    R = pos_series + neg_series
    P = 2 * total_negative_trades * total_positive_trades
    N = len(df_profit)
    try:
        z_score = round((N * (R - 0.5) - P) / ((P * (P - N)) / (N - 1)) ** (1 / 2), 2)
    except ZeroDivisionError:
        z_score = -999

    avg_win = round(df_profit[df_profit > 0].mean(), 2)
    avg_los = round(df_profit[df_profit < 0].mean(), 2)
    prob_win = round(len(df_profit[df_profit > 0]) * 100 / len(df_profit), 2)
    prob_lose = round(100 - prob_win, 2)
    ratio_avg_los = round(df_profit[df_profit > 0].mean() / df_profit[df_profit < 0].abs().mean(), 2)
    label = """
            ---------------------------------------------------------
            | Recovery Factor: {}
            | Profit: {}
            | Max drowdown: {}
            | Z-score: {}
            | Avg. winning trade: {} and Avg. losing trade: {}
            | Probability to win in each trade: {}% ({}% to lose)
            | Ratio Avg. Win:Avg. Loss: {}
            ---------------------------------------------------------
            """.format(recovery_factor, round(balance, 2), round(max_loss, 2),
                       z_score, avg_win, avg_los, prob_win, prob_lose, ratio_avg_los)
    print(label)
    label = 'Recovery Factor: {}\n Profit: {} Max drowdown: {}'.format(recovery_factor, round(balance, 2),
                                                                       round(max_loss, 2))
    if show_chart:
        plt.xlabel(label)
        plt.plot(list_balance)
        plt.show()

    return recovery_factor


# endregion


def strategy(quotes):
    global Lot

    # region ### Get Indicators
    close = np.array(quotes['close'].values, dtype=float)
    rsi = talib.RSI(close, 7)

    # endregion

    # convert timestamp to datetime from quotes df, to new df
    dates = []
    for each in quotes['timestamp']:
        dates.append(datetime.utcfromtimestamp(each / 1000))
    # dates = quotes['timestamp']

    # create report for trades and add header
    report = open('totalReport.csv', 'w+')
    report.write('symbol;index;dateOpen;priceOpen;dateClose;priceClose;profit\n')

    dateOpen = None
    index = 0
    price_open = 0
    is_long = False
    is_short = False

    for item in dates:
        if index < 3:  # because we are using ma[index-3]
            index += 1
            continue

        if not is_short:
            if rsi[index - 2] > 75 and rsi[-1] < 75:
                if is_long:
                    priceClose = float(quotes['open'][index]) * Lot
                    profit = (priceClose - price_open)
                    profit = profit - (profit * 0.01)  # minus fees and slippage
                    profit = round(profit, 4)

                    s = '{};{};{};{};{};{};{}\n'.format("XBTUSD", index, dateOpen, price_open,
                                                        item, priceClose, profit)
                    report.write(s)

                    # reset vars/counters
                    price_open = 0
                    is_long = False

                is_short = True
                dateOpen = item
                price_open = float(quotes['open'][index]) * Lot

        if not is_long:
            if rsi[index - 2] < 25 and rsi[index - 1] > 25:
                if is_short:
                    priceClose = float(quotes['open'][index]) * Lot
                    profit = (price_open - priceClose)
                    profit = profit - (profit * 0.01)  # minus fees and slippage
                    profit = round(profit, 4)

                    s = '{};{};{};{};{};{};{}\n'.format("XBTUSD", index, dateOpen, price_open,
                                                        item, priceClose, profit)
                    report.write(s)

                    # reset vars/counters
                    price_open = 0
                    is_short = False
                is_long = True
                dateOpen = item
                price_open = float(quotes['open'][index]) * Lot

        index += 1
    report.close()


if __name__ == '__main__':
    exchange = ccxt.bitmex()
    since = 1525132800000
    data = exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    since = data[-1][0] + (data[-1][0] - data[-2][0])
    data += exchange.fetch_ohlcv('BTC/USD', timeframe='1h', since=since, limit=500)

    quotes = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # quotes = convert_timeframe(quotes, '15Min')
    #
    # quotes['timestamp'] = quotes.index

    strategy(quotes)
    time.sleep(1)
    show_results()
