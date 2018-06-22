import logging
import sys
from time import sleep
import pandas as pd
from datetime import datetime
from ccxt import errors
from time import sleep


# todo: add order moving


def buy(_symbol, _amount, _rate, _exchange):
    try:

        buy_order = _exchange.create_limit_buy_order(_symbol, _amount, _rate)

        counter = 0
        while len(_exchange.fetch_open_orders(_symbol)) > 0:
            if counter >= 5:
                pass
            counter += 1
            logging.info("Waiting while Buy order fills...")
            sleep(3)

        order_id = buy_order['id']
        price_open = buy_order['price']
        amount = buy_order['amount']

        return {"result": True, "order_id": order_id, "price_open": price_open, 'amount': amount}
    except errors.ExchangeError as e:
        log = 'ExchangeError while trying to buy. {}'.format(e)
        logging.info(log)
        sleep(60)
        buy(_symbol, _amount, _rate, _exchange)
    except Exception as e:
        log = 'Exception! Exchange.py at line {}, {}, {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        logging.info(log)
        return {"result": False, "order_id": None, "price_open": None, 'amount': None}


def sell(_symbol, _amount, _rate, _exchange):
    try:

        sell_order = _exchange.create_limit_sell_order(_symbol, _amount, _rate)

        counter = 0
        while len(_exchange.fetch_open_orders(_symbol)) > 0:
            if counter >= 5:
                pass
            counter += 1
            logging.info("Waiting while Sell order fills...")
            sleep(3)

        order_id = sell_order['id']
        price_open = sell_order['price']
        amount = sell_order['amount']
        return {"result": True, "order_id": order_id, "price_open": price_open, 'amount': amount}
    except errors.ExchangeError as e:
        log = 'ExchangeError while trying to sell. {}'.format(e)
        logging.info(log)
        sleep(60)
        sell(_symbol, _amount, _rate, _exchange)
    except Exception as e:
        log = 'Exception! Exchange.py at line {}, {}, {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        logging.info(log)
        return {"result": False, "order_id": None, "price_open": None, 'amount': None}


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
