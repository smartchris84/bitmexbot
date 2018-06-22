# -*- coding: utf-8 -*-
import logging
import sys
import time
from datetime import datetime

import ccxt
import numpy as np
import pandas as pd
import talib

from bot import config
from bot import exchange
from db import configs
from db import trade


class Strategy:
    def __init__(self):
        conf = configs.read()
        api, secret = conf['API_KEY'], conf['API_SECRET']
        self.bitmex = ccxt.bitmex({'apiKey': api, 'secret': secret})
        # self.bitmex.urls['api'] = self.bitmex.urls['test']  # comment if want to trade at mainnet
        self.symbol = 'BTC/USD'
        self.longed = False
        self.shorted = False
        self.timeframe = conf['TIMEFRAME']
        logging.info('Timeframe: {}'.format(self.timeframe))

        # sl
        try:
            self.sl_percent = conf['SL_PERCENT'] / 100
        except Exception:
            self.sl_percent = None

        # tp
        try:
            self.tp_percent = conf['TP_PERCENT'] / 100
        except Exception:
            self.tp_percent = None

        self.RSI_TOP = conf['RSI_TOP']
        self.RSI_BOT = conf['RSI_BOT']
        self.sl_lvl = -1
        self.tp_lvl = -1
        self.leverage = conf['LEVERAGE']
        self.bitmex.private_post_position_leverage(
            {'symbol': 'XBTUSD', 'leverage': self.leverage + 8})  # setup leverage
        self.amount = self.get_amount()
        self.last_minute = -1
        self.date_open = None
        self.price_open = 0
        self.last_price_close = 0

    def get_amount(self):
        order_book = self.bitmex.fetch_order_book(self.symbol, limit=5)
        btc_price = float(order_book['bids'][0][0])
        balance_btc = self.bitmex.fetch_free_balance()['BTC']
        # balance_usd = balance_btc * btc_price
        percent = configs.read()['PERCENT_TO_TRADE'] / 100
        amount_to_trade = int(balance_btc * percent * self.leverage * btc_price)
        return amount_to_trade

    def save_vars(self):
        trade.update(self.symbol, longed=self.longed, shorted=self.shorted, timeframe=self.timeframe,
                     sl_lvl=self.sl_lvl, tp_lvl=self.tp_lvl, amount=self.amount, date_open=self.date_open,
                     price_open=self.price_open, last_price_close=self.last_price_close)

    def bar_control(self):
        """
        Possible values:
            * 1Min
            * 5Min
            * 15Min
            * 30Min
            * 60Min
        :return:
        """
        timeframe_minutes = int(self.timeframe.split('M')[0])
        min_now = datetime.now().minute
        return min_now % timeframe_minutes == 0 and min_now != self.last_minute

    def on_tick(self):
        try:
            # sl/tp control
            if self.longed and (self.sl_percent or self.tp_percent):
                order_book = self.bitmex.fetch_order_book(self.symbol, limit=5)
                last_price = float(order_book['asks'][0][0])

                # close long by tp or sl
                if last_price >= self.tp_lvl or last_price <= self.sl_lvl:
                    order_book = self.bitmex.fetch_order_book(self.symbol, limit=5)
                    bid = float(order_book['bids'][0][0]) - 3

                    sell_order = exchange.sell(self.symbol, self.amount, bid, self.bitmex)
                    if 'result' in sell_order and sell_order['result']:
                        self.longed = False
                        self.shorted = False

                        price_open = sell_order['price_open']
                        self.last_price_close = price_open

                        # setup sl and tp if it's defined
                        trade_side = 'TP'
                        if last_price <= self.sl_lvl:
                            trade_side = 'SL'

                        logs = '### {}: Long closed by {}; {} contracts at {}'.format(self.symbol, trade_side,
                                                                                      self.amount, price_open)
                        logging.info(logs)
                        print(logs)
            if self.shorted and (self.sl_percent or self.tp_percent):
                order_book = self.bitmex.fetch_order_book(self.symbol, limit=5)
                last_price = float(order_book['asks'][0][0])

                # close short by tp or sl
                if last_price <= self.tp_lvl or last_price >= self.sl_lvl:
                    order_book = self.bitmex.fetch_order_book(self.symbol, limit=5)
                    ask = float(order_book['asks'][0][0]) + 3.5

                    buy_order = exchange.buy(self.symbol, self.amount, ask, self.bitmex)
                    if 'result' in buy_order and buy_order['result']:
                        price_open = buy_order['price_open']
                        self.last_price_close = price_open

                        self.longed = False
                        self.shorted = False

                        trade_side = 'TP'
                        if last_price >= self.sl_lvl:
                            trade_side = 'SL'

                        logs = '### {}: Long closed by {}; {} contracts at {}'.format(self.symbol, trade_side,
                                                                                      self.amount, price_open)
                        logging.info(logs)
                        print(logs)

            # region ### ======== Bar Control ======== ###
            if not self.bar_control():
                return False
            self.last_minute = datetime.now().minute

            # endregion

            if self.timeframe == '1Min':
                since = (int(time.time()) - 10000) * 1000
            elif self.timeframe == '60Min':
                since = (int(time.time()) - 100000) * 1000
            else:
                since = (int(time.time()) - 30000) * 1000

            data = pd.DataFrame(self.bitmex.fetch_ohlcv(self.symbol, '1m', since=since, limit=500),
                                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            quotes = exchange.convert_timeframe(data, self.timeframe)

            # region ### ======== Get Indicators ======== ###
            close = np.array(quotes['close'].values, dtype=float)
            rsi = talib.RSI(close, config.RSI_PERIOD)
            # endregion

            # region ### ======== Close long / Open short  POSITION ======== ###
            if not self.shorted:
                if rsi[-3] > self.RSI_TOP > rsi[-2]:  # short signal
                    logging.info("rsi[-3]({}) > {} and rsi[-2]({}) < {}".format(rsi[-3], self.RSI_TOP, rsi[-2],
                                                                                self.RSI_TOP))

                    # get bid price
                    order_book = self.bitmex.fetch_order_book(self.symbol, limit=5)
                    bid = float(order_book['bids'][0][0]) - 3

                    if self.longed:
                        amount = self.amount * 2
                    else:
                        amount = self.amount

                    sell_order = exchange.sell(self.symbol, amount, bid, self.bitmex)
                    if 'result' in sell_order and sell_order['result']:
                        self.price_open = sell_order['price_open']
                        self.date_open = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                        if self.longed:
                            self.last_price_close = self.price_open

                        self.longed = False
                        self.shorted = True

                        # setup sl and tp if it's defined
                        if self.sl_percent:
                            self.sl_lvl = self.price_open + (self.price_open * self.sl_percent)
                        if self.tp_percent:
                            self.tp_lvl = self.price_open - (self.price_open * self.tp_percent)

                        logs = '### {}: Shorted {} contracts at {}. SL: {}; TP: {}'.format(self.symbol, amount,
                                                                                           self.price_open,
                                                                                           self.sl_lvl, self.tp_lvl)
                        logging.info(logs)
                        print(logs)

            # endregion

            # region ### ======== Open Long / Close short Position ======== ###
            if not self.longed:
                if rsi[-3] < self.RSI_BOT < rsi[-2]:  # long signal
                    logging.info("rsi[-3]({}) < {} and rsi[-2]({}) > {}".format(rsi[-3], self.RSI_BOT, rsi[-2],
                                                                                self.RSI_BOT))

                    # get ask price
                    order_book = self.bitmex.fetch_order_book(self.symbol, limit=5)
                    ask = float(order_book['asks'][0][0]) + 3.5  # magic number

                    if self.shorted:
                        amount = self.amount * 2
                    else:
                        amount = self.amount

                    buy_order = exchange.buy(self.symbol, amount, ask, self.bitmex)
                    if 'result' in buy_order and buy_order['result']:
                        self.price_open = buy_order['price_open']
                        self.date_open = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        if self.shorted:
                            self.last_price_close = self.price_open
                        self.longed = True
                        self.shorted = False

                        # setup sl and tp if it's defined
                        if self.sl_percent:
                            self.sl_lvl = self.price_open - (self.price_open * self.sl_percent)
                        if self.tp_percent:
                            self.tp_lvl = self.price_open + (self.price_open * self.tp_percent)

                        logs = '### {}: Longed {} contracts at {}; SL: {}; TP: {}'.format(self.symbol, amount,
                                                                                          self.price_open, self.sl_lvl,
                                                                                          self.tp_lvl)
                        logging.info(logs)
                        print(logs)
            # endregion
            self.save_vars()
            return True
        except Exception as e:
            log = 'Exception! Strategy.py at line {}, {}, {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
            print(log)
            logging.info(log)
            return False
