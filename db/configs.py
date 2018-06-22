import logging
import sys

from sqlalchemy import Column, TEXT, FLOAT, BOOLEAN
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import DB_CONNECTION

db = create_engine(DB_CONNECTION, pool_size=30, max_overflow=100)
base = declarative_base()


class Configs(base):
    __tablename__ = 'configs'

    IS_RUNNING = Column(BOOLEAN, primary_key=True)
    PERCENT_TO_TRADE = Column(FLOAT)
    API_KEY = Column(TEXT)
    API_SECRET = Column(TEXT)
    UPDATED = Column(BOOLEAN)
    TIMEFRAME = Column(TEXT)
    LEVERAGE = Column(FLOAT)
    SL_PERCENT = Column(FLOAT)
    TP_PERCENT = Column(FLOAT)
    RSI_TOP = Column(FLOAT, nullable=False)
    RSI_BOT = Column(FLOAT, nullable=False)


def create():
    raise NotImplemented


def read():
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)

    rows = session.query(Configs)
    for item in rows:
        sl_percent = item.SL_PERCENT
        if sl_percent == 0:
            sl_percent = None
        tp_percent = item.TP_PERCENT
        if tp_percent == 0:
            tp_percent = None

        t = {
            'IS_RUNNING': item.IS_RUNNING,
            'PERCENT_TO_TRADE': item.PERCENT_TO_TRADE,
            'API_KEY': item.API_KEY,
            'API_SECRET': item.API_SECRET,
            'UPDATED': item.UPDATED,
            'TIMEFRAME': item.TIMEFRAME,
            'LEVERAGE': item.LEVERAGE,
            'SL_PERCENT': sl_percent,
            'TP_PERCENT': tp_percent,
            'RSI_TOP': item.RSI_TOP,
            'RSI_BOT': item.RSI_BOT,
        }
        return t
    return None


def update(is_running=None, percent_to_trade=None, api_key=None, api_secret=None, updated=None,
           timeframe=None, leverage=None, sl_percent=None, tp_percent=None, rsi_top=None, rsi_bot=None):
    try:
        Session = sessionmaker(db)
        session = Session()
        base.metadata.create_all(db)

        rows = session.query(Configs)

        for item in rows:
            if is_running is not None:
                item.IS_RUNNING = is_running
            if percent_to_trade:
                item.PERCENT_TO_TRADE = percent_to_trade
            if api_key:
                item.API_KEY = api_key
            if api_secret:
                item.API_SECRET = api_secret
            if updated is not None:
                item.UPDATED = updated
            if timeframe:
                item.TIMEFRAME = timeframe
            if leverage:
                item.LEVERAGE = leverage
            if sl_percent:
                item.SL_PERCENT = sl_percent
            if tp_percent:
                item.TP_PERCENT = tp_percent
            if rsi_top:
                item.RSI_TOP = rsi_top
            if rsi_bot:
                item.RSI_BOT = rsi_bot
            break
        session.commit()
        return True
    except Exception as e:
        log = 'Got Exception! Error on line {}, {}, {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        print(log)
        logging.info(log)
        return False
