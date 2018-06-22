import logging
import sys

from sqlalchemy import Column, TEXT, FLOAT, BOOLEAN, TIMESTAMP
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db import DB_CONNECTION

db = create_engine(DB_CONNECTION, pool_size=30, max_overflow=100)
base = declarative_base()


class Trade(base):
    __tablename__ = 'trade'

    symbol = Column(TEXT, primary_key=True)
    longed = Column(BOOLEAN)
    shorted = Column(BOOLEAN)
    timeframe = Column(TEXT)
    sl_lvl = Column(FLOAT)
    tp_lvl = Column(FLOAT)
    amount = Column(FLOAT)
    date_open = Column(TIMESTAMP)
    price_open = Column(FLOAT)
    last_price_close = Column(FLOAT)


def create():
    raise NotImplemented


def read():
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)

    rows = session.query(Trade)
    for item in rows:
        t = {
            'symbol': item.symbol,
            'longed': item.longed,
            'shorted': item.shorted,
            'timeframe': item.timeframe,
            'sl_lvl': item.sl_lvl,
            'tp_lvl': item.tp_lvl,
            'amount': item.amount,
            'date_open': item.date_open,
            'price_open': item.price_open,
            'last_price_close': item.last_price_close,
        }
        return t
    return None


def update(symbol='BTC/USD', longed=False, shorted=False, timeframe=None, sl_lvl=-1, tp_lvl=-1, amount=0,
           date_open=None, price_open=0, last_price_close=0):
    try:
        Session = sessionmaker(db)
        session = Session()
        base.metadata.create_all(db)

        rows = session.query(Trade)

        for item in rows:
            if item.symbol == symbol:
                item.longed = longed
                item.shorted = shorted
                item.timeframe = timeframe
                item.sl_lvl = sl_lvl
                item.tp_lvl = tp_lvl
                item.amount = amount
                item.date_open = date_open
                item.price_open = price_open
                item.last_price_close = last_price_close
            break
        session.commit()
        return True
    except Exception as e:
        log = 'Got Exception! Error on line {}, {}, {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        print(log)
        logging.info(log)
        return False
