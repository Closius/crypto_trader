import os
import sys
import datetime
import time
import traceback
import logging

from btfxwss import BtfxWss
from django.db import connection

# Setup Django
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DJANGO_SETTINGS_MODULE"] = "server.settings"
django.setup()

from management_app.models import Pair_Timeframe
from server.settings import BASE_DIR


def upsert(data, pairs_timeframes_id):
    """
        ON CONFLICT affects field which has some constraint like unique. Otherwise it raises an error
    """
    if len(data) == 0:
        return None

    for d in data:
        f = "(%s, '%s', %s, %s, %s, %s, %s)" % (pairs_timeframes_id, d["mts"], d["open"], d["close"], d["high"], d["low"], d["volume"])
        with connection.cursor() as cursor:
            g = '''
                                    INSERT INTO candle (
                                      pair_timeframe_id, mts, open, close, high, low, volume
                                      ) VALUES %s
                                      ON CONFLICT (pair_timeframe_id, mts)
                                      DO UPDATE SET
                                            open = EXCLUDED.open,
                                            close = EXCLUDED.close,
                                            high = EXCLUDED.high,
                                            low = EXCLUDED.low,
                                            volume = EXCLUDED.volume;
            ''' % f
            cursor.execute(g)

    time.sleep(0.3)
    return None

def should_update(current_mts, last_mts, pairs_timeframes_id):
    try:
        if current_mts >= last_mts[pairs_timeframes_id]:
            last_mts[pairs_timeframes_id] = current_mts
            return True
        else:
            return False
    except Exception:
        last_mts[pairs_timeframes_id] = current_mts
        return True

def main(logger):

    # Fetch available pairs & timeframes from DB
    pairs_timeframes = Pair_Timeframe.objects.all()

    if pairs_timeframes.exists() is False:
        logger.error("No pairs in a database.")
        return None

    wss = BtfxWss()
    wss.start()
    time.sleep(1)  # give the client some prep time to set itself up

    last_mts = dict()

    pairs_timeframes_tuples = pairs_timeframes.values_list("id", "pair", "timeframe")
    for pairs_timeframes_id, pair, timeframe in pairs_timeframes_tuples:
        wss.subscribe_to_candles(pair, timeframe=timeframe)
        last_mts.update({pairs_timeframes_id: None})
    time.sleep(5)
    candles_queue = {}
    for pairs_timeframes_id, pair, timeframe in pairs_timeframes_tuples:
        candles_queue.update({pair + timeframe: wss.candles(pair=pair, timeframe=timeframe) })
        logger.info("Collecting CANDLES of pair '%s' with timeframe '%s' has been started" % (pair, timeframe))


    try:
        while True:

            for pairs_timeframes_id, pair, timeframe in pairs_timeframes_tuples:
                if not candles_queue[pair + timeframe].empty():

                    q_candles = candles_queue[pair + timeframe].get()

                    """
                    ([  [4345.5, 16.7770791, 4345.6, 12.74414776, 77.6, 0.0182, 4345.6, 15220.55529737, 4397.5, 4248.4] ], 1503992628.42302)

                    # MTS     int     millisecond time stamp
                    # OPEN    float   First execution during the time frame
                    # CLOSE   float   Last execution during the time frame
                    # HIGH    integer     Highest execution during the time frame
                    # LOW     float   Lowest execution during the timeframe
                    # VOLUME  float   Quantity of symbol traded within the timeframe
                    """

                    data = []

                    if isinstance(q_candles[0][0][0], list):
                        mass = sorted(q_candles[0][0], key=lambda x: x[0])
                        for c in mass:
                            mts = datetime.datetime.utcfromtimestamp(float(str(c[0])[:-3]))
                            if should_update(mts, last_mts, pairs_timeframes_id):
                                data.append({
                                    "mts":    mts,
                                    "open":   c[1],
                                    "close":  c[2],
                                    "high":   c[3],
                                    "low":    c[4],
                                    "volume": c[5]
                                })
                    else:
                        mts = datetime.datetime.utcfromtimestamp(float(str(q_candles[0][0][0])[:-3]))
                        if should_update(mts, last_mts, pairs_timeframes_id):
                            data.append({
                                "mts":    mts,
                                "open":   q_candles[0][0][1],
                                "close":  q_candles[0][0][2],
                                "high":   q_candles[0][0][3],
                                "low":    q_candles[0][0][4],
                                "volume": q_candles[0][0][5]
                            })

                    # Important:
                    # UPSERT works well.
                    # If you have missed rows -> check volume
                    upsert(data=data, pairs_timeframes_id=pairs_timeframes_id)

    except Exception:
        logger.error(str(traceback.format_exc()))


    for pairs_timeframes_id, pair, timeframe in pairs_timeframes_tuples:
        wss.unsubscribe_from_candles(pair, timeframe=timeframe)

    # Shutting down the client
    wss.stop()
    logger.info("Process terminated")

if __name__ == '__main__':
    logger = logging.getLogger('collector')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    log_file = os.path.join(BASE_DIR, "logs", "log", "collect_data.log")
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    try:
        main(logger)
    except Exception:
        logger.error(str(traceback.format_exc()))