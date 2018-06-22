import logging
import time
import sys
from bot import config
from bot import strategy

from db import configs

strategy_instance = None
is_once = False


def on_init():
    # ### Setup logging settings
    if config.SAVE_LOGS is False:
        logging.FileHandler('logs.log', mode='w')  # remove previous logs

    logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s :>>>  %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    log = logging.getLogger(__name__)
    fh = logging.FileHandler('logs.log')
    fh.setLevel(logging.INFO)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    log.addHandler(sh)
    log.addHandler(fh)

    logs = 'Bot launched'
    logging.info(logs)
    print(logs)

    # ### Initialize trading symbols
    global strategy_instance

    strategy_instance = strategy.Strategy()
    logs = 'RSI Strategy initialized'
    logging.info(logs)
    print(logs)

    # end of init

    logs = '===== Start trading ====='
    logging.info(logs)
    print(logs)


if __name__ == '__main__':

    # initialize all settings before launch bot
    on_init()

    while True:
        try:
            conf = configs.read()
            bot_running = conf['IS_RUNNING']
            bot_updated = conf['UPDATED']
            if bot_running:
                if not bot_updated:
                    configs.update(updated=True)
                    is_once = False
                    del strategy_instance
                    strategy_instance = strategy.Strategy()
                    logging.info("Configs UPDATED: True. PERCENT_TO_TRADE: {}; TIMEFRAME: "
                                 "{}; LEVERAGE: {}; SL_PERCENT: {}; TP_PERCENT: {} \n"
                                 "RSI_TOP: {}; RSI_BOT: {}"
                                 .format(conf['PERCENT_TO_TRADE'], conf['TIMEFRAME'], conf['LEVERAGE'],
                                         conf['SL_PERCENT'], conf['TP_PERCENT'], conf['RSI_TOP'], conf['RSI_BOT']))
            else:
                configs.update(updated=False)
                if not is_once:
                    logging.info("Configs UPDATED: False")
                    is_once = True
                time.sleep(30)
                continue

            strategy_instance.on_tick()
            time.sleep(10)
        except Exception as e:
            log = 'Got exception at main.py: {}'.format(e)
            print(log)
            logging.info(log)
            time.sleep(60)
            continue
