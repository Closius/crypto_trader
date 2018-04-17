import sys
import os
import traceback
import time
import datetime
import math

import numpy as np

# Setup Django
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DJANGO_SETTINGS_MODULE"] = "server.settings"
django.setup()
from management_app.models import Pair_Timeframe, Candle, Trade, Orders_History
from management_app.views import collector_misc

from trader import bitfinex_client
from trader.strategy import Strategy

import logging
logger = logging.getLogger('crypto_trader_bot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

from server.settings import BASE_DIR

def log_info(msg):
    logger.info(msg)

def check_collecor_is_running(date, timeframe):

    if not hasattr(check_collecor_is_running, "wait_delay"):
        setattr(check_collecor_is_running, "wait_delay", datetime.datetime.utcnow())
        setattr(check_collecor_is_running, "previous_last_date", date[-1])
        if "m" in timeframe:
            wait_period = int(timeframe[:-1])
        elif "h" in timeframe:
            wait_period = int(timeframe[:-1]) * 60
        elif "d" in timeframe:
            wait_period = int(timeframe[:-1]) * 60 * 24
        p = math.ceil(wait_period * 1.35)
        p = 3 if p < 15 else p
        setattr(check_collecor_is_running, "wait_period", p)
        return

    if (datetime.datetime.utcnow() - check_collecor_is_running.wait_delay) < datetime.timedelta(minutes=check_collecor_is_running.wait_period):
        return

    if check_collecor_is_running.previous_last_date == date[-1]:
        should_restart = True
        while should_restart:
            # Restart
            collector_misc("stop")
            time.sleep(2)
            collector_misc("start")
            time.sleep(10)
            d = collector_misc("status")  # TODO: might be not good
            if d["is_alive"] == True:
                should_restart = False
        log_info("====================================================================")
        log_info("====================================================================")
        log_info("====================================================================")
        log_info("")
        log_info("")
        log_info("")
        log_info("                     Collector has been restarted")
        log_info("")
        log_info("")
        log_info("")
        log_info("====================================================================")
        log_info("====================================================================")
        log_info("====================================================================")
    check_collecor_is_running.wait_delay = datetime.datetime.utcnow()
    check_collecor_is_running.previous_last_date = date[-1]
    return

def get_balance(currency, low_limit):
    available = 0.0
    b = bitfinex_client.post_balances(show_console=True)
    for w in b:
        if (w["type"] == "exchange") and (w["currency"] == currency.lower()):
            available = float(w["available"])
            break
    if available < low_limit:
        available = 0.0
    return available

def wait_delay(delay):
    log_info("\n +++ Wait %ss +++\n" % str(delay))
    time.sleep(delay)

def start_order(pair, amount, price, side, order_type, show_console, divided_BTC_wallet_current, divided_USD_wallet_current, index):


    def get_balance():
        USD_wallet = 0.0
        BTC_wallet = 0.0
        b = bitfinex_client.post_balances(show_console=True)
        for w in b:
            if (w["type"] == "exchange") and (w["currency"] == pair[3:].lower()):
                USD_wallet = float(w["available"])
            if (w["type"] == "exchange") and (w["currency"] == pair[:3].lower()):
                BTC_wallet = float(w["available"])

        low_limit = 0.000001
        if USD_wallet < low_limit:
            USD_wallet = 0.0
        if BTC_wallet < low_limit:
            BTC_wallet = 0.0   
        return USD_wallet, BTC_wallet     

    def wallet_correction(divided_wallet_current, wallet_init, wallet_current, index, currency):

        log_info("--------------------- WALLET CORRECTION ---------------------")
        log_info("             Wallet parts correction for %s:" % currency)
        log_info("")
        log_info("")
        # Refresh parts amounts. Proportional
        DIV_PARTS = len(divided_wallet_current)

        log_info("divided_wallet_current before: " + str(divided_wallet_current))
        log_info("wallet_init: " + str(wallet_init))
        log_info("wallet_current: " + str(wallet_current))
        log_info("wallet_init - wallet_current (must be > 0): " + str(wallet_init - wallet_current))
        log_info("Current index: " + str(index))
        log_info("")

        if wallet_init > wallet_current:
            remains_for_each_wallet_except_index = wallet_current / (DIV_PARTS-1)
            for i in range(len(divided_wallet_current)):
                if (i != index) and (divided_wallet_current[i] != 0.0):
                    divided_wallet_current[i] = remains_for_each_wallet_except_index
                elif i == index:
                    divided_wallet_current[i] = 0.0
        else:
            remains_for_each_wallet_except_index = wallet_init / (DIV_PARTS-1)
            current_part = wallet_current - wallet_init
            for i in range(len(divided_wallet_current)):
                if (i != index) and (divided_wallet_current[i] != 0.0):
                    divided_wallet_current[i] = remains_for_each_wallet_except_index
                elif i == index:
                    divided_wallet_current[i] = current_part

        log_info("CORRECTED divided_wallet_current: " + str(divided_wallet_current))
        log_info("----------------------------------------------------------")
        log_info("")
        log_info("")

        return divided_wallet_current

    log_info("")
    log_info("")
    log_info("")
    log_info("--------> Current BTC divided wallet: " + str(divided_BTC_wallet_current))
    log_info("--------> Current USD divided wallet: " + str(divided_USD_wallet_current))

    if side == 'sell':
        log_info('''



                                    =======================================
                                    \                                     /
                                     \                                   /
                                      \                                 /
                                       \                               /
                                        \                             /
                                         \                           /
                                          \         S E L L         /
                                           \                       /
                                            \                     /
                                             \                   /
                                              \                 /
                                               \               /
                                                \             /
                                                 \           /
                                                  \         /
                                                   \       /
                                                    \     /
                                                     \   /
                                                      \ / 



            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================


        ''')
    elif side == 'buy':
        log_info('''


                                                       / \\
                                                      /   \\
                                                     /     \\
                                                    /       \\
                                                   /         \\
                                                  /           \\
                                                 /             \\
                                                /               \\
                                               /                 \\
                                              /                   \\
                                             /                     \\
                                            /                       \\
                                           /          B U Y          \\
                                          /                           \\
                                         /                             \\
                                        /                               \\
                                       /                                 \\
                                      /                                   \\
                                     /                                     \\
                                     =======================================   



            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================


        ''')
    

    # Get balance for checking trade history at the end
    USD_wallet_init, BTC_wallet_init = get_balance()

    new_order = bitfinex_client.order(symbol=pair, amount=amount, price=price, side=side, order_type=order_type, show_console=show_console)

    if "message" in new_order:
        # {
        #  "message": "Invalid order: minimum size for XMR/USD is 0.2"
        # }
        return None

    wait_delay(delay=5)

    log_info("================ Order executing %s BEGIN" % side.upper() )

    count_of_orders_parts = 0
    while True:
        count_of_orders_parts += 1
        log_info("Attempt " + str(count_of_orders_parts))
        status = bitfinex_client.order_status(order_id=new_order["order_id"], show_console=show_console)
        if "is_live" in status:
            if status["is_live"] is False:
                break
        wait_delay(delay=5)

    log_info("================ Order executing %s END" % side.upper() )

    # TODO: status["remaining_amount"] -> float(status["remaining_amount"])
    #                   "0.234"        ->          "2.34e-1"
    # Because of cast we can miss or get some digits. accuracy
    #
    # Maybe we should store text "0.234" despite number 0.234

    # TODO: I think we can use smaller timedelta
    since_datetime = datetime.datetime.utcfromtimestamp( float(new_order["timestamp"]) ) - datetime.timedelta(seconds=10)
    since_datetime = since_datetime.replace(tzinfo=datetime.timezone.utc)

    until_datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
    until_datetime = until_datetime.replace(tzinfo=datetime.timezone.utc)

    while True:
        trade_hist = bitfinex_client.trade_history(symbol=pair, since_datetime=since_datetime, until_datetime=until_datetime, show_console=show_console)
        # TODO: Probably should calculate and check amount
        if len(trade_hist) > 0:
            break
        wait_delay(delay=5)

    trade_history_amount = 0.0
    trade_history_amount_USD = 0.0
    fee_amount = 0.0
    fee_currency = ""
    for trade in trade_hist:
        if trade["order_id"] == new_order["order_id"]:
            trade_history_amount += float(trade["amount"])
            trade_history_amount_USD += float(trade["amount"]) * float(trade["price"])
            fee_amount += float(trade["fee_amount"])
            fee_currency += trade["fee_currency"] + "  "


    # Get how much we've got
    # TODO: low lomit
    # PAIR orly 6 letters  !!!!!!!!
    wait_delay(delay=20)

    while True:
        USD_wallet, BTC_wallet = get_balance()
        if side == 'sell':
            # Shlould wait for update wallets
            # Prabaly should take into account fee_amount
            if (USD_wallet > USD_wallet_init) and (BTC_wallet < BTC_wallet_init):
                break
        elif side == 'buy':
            if (BTC_wallet > BTC_wallet_init) and (USD_wallet < USD_wallet_init):
                break

    log_info("")
    log_info("divided_BTC_wallet_current before correction: " + str(divided_BTC_wallet_current))
    log_info("divided_USD_wallet_current before correction: " + str(divided_USD_wallet_current))
    log_info("")


    divided_BTC_wallet_current = wallet_correction(divided_wallet_current=divided_BTC_wallet_current, 
        wallet_init=BTC_wallet_init, wallet_current=BTC_wallet, index=index, currency="BTC")

    divided_USD_wallet_current = wallet_correction(divided_wallet_current=divided_USD_wallet_current, 
        wallet_init=USD_wallet_init, wallet_current=USD_wallet, index=index, currency="USD")


    log_info("")
    log_info("divided_BTC_wallet_current after correction: " + str(divided_BTC_wallet_current))
    log_info("divided_USD_wallet_current after correction: " + str(divided_USD_wallet_current))
    log_info("")
    

    price_return = float(status["avg_execution_price"])

    log_info("End %s" % side.upper())
    log_info('''


            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================
            ==========================================================================================


        ''')

    BTC_end = divided_BTC_wallet_current[index]
    USD_end = divided_USD_wallet_current[index]

    return price_return, BTC_end, USD_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current

def sell(pair, amount, price, fee, divided_BTC_wallet_current, divided_USD_wallet_current, index):
    """
        SELL on stock exchage

        If you change order type - check fee's type: TAKER or MAKER

        !!!!!! fee already = fee / 100, fee NOT in %, it is in parts

    """

    amount = amount - (amount * fee)

    log_info("------------------- Amount calculation -------------------")
    log_info("                  for market sell order:")
    log_info("                  (price doesn't matter)")
    log_info("")
    log_info("         Formula: amount = amount - (amount * fee) ")
    log_info("amount: " + str(amount))
    log_info("")
    log_info("----------------------------------------------------------")

    BTC_init = divided_BTC_wallet_current[index]
    USD_init = divided_USD_wallet_current[index]

    price_return, BTC_end, USD_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current = start_order(
        pair=pair, 
        amount=amount, 
        price=99999.0, 
        side='sell', 
        order_type="exchange market", 
        show_console=True,
        divided_BTC_wallet_current=divided_BTC_wallet_current, 
        divided_USD_wallet_current=divided_USD_wallet_current, 
        index=index
    )

    return price_return, BTC_init, USD_init, USD_end, BTC_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current

def buy(pair, how_much_usd_I_want_spend_for_buy, price, fee, divided_BTC_wallet_current, divided_USD_wallet_current, index):
    """
        BUY on stock exchage

        how_much_usd_I_want_spend_for_buy = divided_USD_wallet_current[index]

        If you change order type - check fee's type: TAKER or MAKER

        !!!!!! fee already = fee / 100, fee NOT in %, it is in parts

        Prpbably we can use MARKET BUY. But I tested it on STOP BUY 

        !!!!!!!!!!!!!!!!
        Better to do STOP-LIMIT. Because STOP order can try to buy for market price on the stop moment. 
        The price on the stop moment can be either less than given price or higher than one!
        As a result a current buy order can be executed on higher price that you set.
        In order to avoid it better to use STOP-LIMIT order

        Moreover we can create a buy order many times. Try to buy for 5-10 attempts.

    """

    ticker = bitfinex_client.get_ticker(pair=pair, show_console=True)
    current_best_bid_fresh = float(ticker["bid"])

    # price must be less that price_for_calc_amount
    price = current_best_bid_fresh - ((current_best_bid_fresh * fee) * 2 ) # TODO: 2 - is an insurance. Probably it could be decreased or removed 
    price_for_calc_amount = current_best_bid_fresh - (current_best_bid_fresh * fee)
    amount = how_much_usd_I_want_spend_for_buy / price_for_calc_amount

    log_info("--------------- Amount & Price calculation ---------------")
    log_info("                   for stop buy order:")
    log_info("")
    log_info("""    Formula: (price * amount) + (price * amount * fee) <= how_much_usd_I_want_spend_for_buy")

        price_for_calc_amount = current_best_bid - (current_best_bid * fee)
        amount = how_much_usd_I_want_spend_for_buy / price_for_calc_amount
        
        price = current_best_bid - ((current_best_bid * fee) * 2 )
            2 - is an insurance, for any cases. Probably it could be decreased or removed ")
    """)
    log_info("current_best_bid: " + str(current_best_bid_fresh))
    log_info("how_much_usd_I_want_spend_for_buy: " + str(how_much_usd_I_want_spend_for_buy))
    log_info("amount: " + str(amount))
    log_info("price: " + str(price))
    log_info("fee (% / 100): " + str(fee))
    log_info("Fee in USD")
    log_info("")
    log_info("")
    log_info("(price * amount) + (price * amount * fee): " + str((price * amount) + (price * amount * fee)))
    log_info("how_much_usd_I_want_spend_for_buy - ((price * amount) + (price * amount * fee)): " + str(how_much_usd_I_want_spend_for_buy - ((price * amount) + (price * amount * fee))))
    log_info("")
    log_info("")
    log_info("----------------------------------------------------------")


    BTC_init = divided_BTC_wallet_current[index] # = how_much_usd_I_want_spend_for_buy
    USD_init = divided_USD_wallet_current[index]

    price_return, BTC_end, USD_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current = start_order(
        pair=pair, 
        amount=amount, 
        price=price, 
        side='buy', 
        order_type="exchange stop", 
        show_console=True,
        divided_BTC_wallet_current=divided_BTC_wallet_current, 
        divided_USD_wallet_current=divided_USD_wallet_current, 
        index=index
    )

    return price_return, BTC_init, USD_init, USD_end, BTC_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current

def insert_trader_db(trade_id, mts, wallet_index, price, amount, usd_init_in_wallet, btc_init_in_wallet, 
    usd_end_in_wallet, btc_end_in_wallet, fee_amount, fee_currency, loss, misc, pair, kind):

    orders_history = Orders_History(trade_id=trade_id)

    orders_history.mts                     = mts
    orders_history.wallet_index            = wallet_index
    orders_history.price                   = price
    orders_history.amount                  = amount
    orders_history.fee_amount              = fee_amount
    orders_history.fee_currency            = fee_currency
    orders_history.loss                    = loss
    orders_history.misc                    = misc
    orders_history.kind                    = kind
    orders_history.usd_init_in_wallet      = usd_init_in_wallet
    orders_history.btc_init_in_wallet      = btc_init_in_wallet
    orders_history.usd_end_in_wallet       = usd_end_in_wallet
    orders_history.btc_end_in_wallet       = btc_end_in_wallet

    orders_history.save()
    pass

def get_candles_data(pair_timeframe, begin_time):
    candles = Candle.objects.filter(pair_timeframe=pair_timeframe, mts__gte=begin_time).order_by('mts')

    date = np.array([])
    openp = np.array([])
    closep = np.array([])
    highp = np.array([])
    lowp = np.array([])
    volumep = np.array([])

    for c in candles:
        date = np.append(date, [c.mts])
        openp = np.append(openp, [float(c.open)])
        closep = np.append(closep, [float(c.close)])
        highp = np.append(highp, [float(c.high)])
        lowp = np.append(lowp, [float(c.low)])
        volumep = np.append(volumep, [float(c.volume)])

    return date, openp, closep, highp, lowp, volumep



def main(trader_parms):

    pair = trader_parms["pair"]

    pair_timeframe = Pair_Timeframe.objects.get(pair=pair, timeframe=trader_parms["timeframe"])

    # Include a history data for better TEMA calculation and other 
    begin_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=60*24*3)

    date, openp, closep, highp, lowp, volumep = get_candles_data(pair_timeframe, begin_time)

    _candle_price = highp[-1] - (highp[-1] - lowp[-1])/2

    if trader_parms["init_last_sell_price"] == "inherit":
        init_last_sell_price = _candle_price
    else:
        init_last_sell_price = trader_parms["init_last_sell_price"]

    if trader_parms["init_last_buy_price"] == "inherit":
        init_last_buy_price = _candle_price
    else:
        init_last_buy_price = trader_parms["init_last_buy_price"]

    # TODO: low limit
    # TODO: one request
    initial_USD_wallet = get_balance(currency=pair[3:], low_limit=0.001)
    initial_BTC_wallet = get_balance(currency=pair[:3], low_limit=0.004)

    # TODO: Check minimun order size for this pair

    # Create Trade record
    trade = Trade(pair_timeframe=pair_timeframe)

    trade.timeperiod                                  = trader_parms["timeperiod"]
    trade.independent_last_sell_buy_price_checking    = trader_parms["independent_last_sell_buy_price_checking"]
    trade.forse_commit_sell_buy_status_distace        = trader_parms["forse_commit_sell_buy_status_distace"] 
    trade.LPP_count                                   = trader_parms["LPP_count"]
    trade.EP_gradient_threshold                       = trader_parms["EP_gradient_threshold"]
    trade.LPP_gradients_threshold                     = trader_parms["LPP_gradients_threshold"]
    trade.sell_threshold                              = trader_parms["sell_threshold"]
    trade.buy_threshold                               = trader_parms["buy_threshold"]
    trade.statistic_begin_time                        = date[0]
    trade.trading_begin_time                          = datetime.datetime.utcnow()
    trade.trading_end_time                            = None 
    trade.is_active                                   = True
    trade.init_last_sell_price                        = init_last_sell_price 
    trade.init_last_buy_price                         = init_last_buy_price 
    trade.initial_BTC_wallet                          = initial_BTC_wallet 
    trade.initial_USD_wallet                          = initial_USD_wallet 
    trade.div_parts                                   = trader_parms["DIV_PARTS"]

    trade.save()

    strategy = Strategy(
                    date                                    = date,
                    init_last_sell_price                    = float(trade.init_last_sell_price),
                    init_last_buy_price                     = float(trade.init_last_buy_price),
                    initial_BTC_wallet                      = float(trade.initial_BTC_wallet),
                    initial_USD_wallet                      = float(trade.initial_USD_wallet),
                    DIV_PARTS                               = trade.div_parts, 
                    timeperiod_TEMA                         = trade.timeperiod,
                    verbose                                 = True,
                    LPP_count                               = trade.LPP_count,
                    EP_gradient_threshold                   = float(trade.EP_gradient_threshold),
                    LPP_gradients_threshold                 = float(trade.LPP_gradients_threshold),
                    sell_threshold                          = float(trade.sell_threshold),
                    buy_threshold                           = float(trade.buy_threshold),
                    production                              = True,
                    independent_last_sell_buy               = trade.independent_last_sell_buy_price_checking,
                                                              # TODO: If not None it is a Decimal
                    forse_commit_sell_buy_status_distace    = trade.forse_commit_sell_buy_status_distace,
                    pair                                    = trade.pair_timeframe.pair,
                    trade_id                                = trade.id
    )

    log_info("")
    log_info("")
    log_info("                       START TRADER")

    strategy.sell = sell
    strategy.buy = buy
    strategy.insert_trader_db = insert_trader_db

    i = 0 
    wait_datetime = datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
    try:
        while True:

            time.sleep(5)
            i += 1
            log_info("Check: " + str(i))

            # Get fees
            if (datetime.datetime.utcnow() - wait_datetime) >= datetime.timedelta(seconds=60):
                wait_datetime = datetime.datetime.utcnow()
                fees = bitfinex_client.post_account_info(show_console=False)
                for fee in fees[0]["fees"]:
                    # TODO: Only 3 simbols TIKERS !!!!!!
                    if fee["pairs"] == pair[:3]:
                        maker_fee = fee["maker_fees"]
                        taker_fee = fee["taker_fees"]


            begin_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=60*24*2)

            date, openp, closep, highp, lowp, volumep = get_candles_data(pair_timeframe, begin_time)

            # Get current price
            if trade.pair_timeframe.timeframe != "1m":
                candles = Candle.objects.filter(pair_timeframe=pair_timeframe).latest('mts')
                date_1m = candles.mts
                closep_1m = candles.close
            else:
                date_1m = date
                closep_1m = closep

            if len(date_1m) == 0:
                continue
            current_best_ask = closep_1m[-1]
            current_best_bid = closep_1m[-1]

            candle_price = highp + (highp - lowp)/2
            strategy.calculate(last_N_candle_prices=candle_price,
                las_N_current_date=date,
                current_best_ask=current_best_ask,
                current_best_bid=current_best_bid,
                maker_fee = maker_fee,
                taker_fee = taker_fee)


            check_collecor_is_running(date=date, timeframe=trader_parms["timeframe"])


    except Exception:
        logger.error(str(traceback.format_exc()))
        trade.trading_end_time = datetime.datetime.utcnow()
        trade.is_active = False
        trade.save()

if __name__ == '__main__':

    trader_parms = {
        "pair": str(sys.argv[1]).upper(),
        "timeframe": str(sys.argv[2]),
        "timeperiod": int(sys.argv[3]),
        "independent_last_sell_buy_price_checking": True if str(sys.argv[4]) == "True" else False,
        "forse_commit_sell_buy_status_distace": str(sys.argv[5]) if str(sys.argv[5]) != "None" else None,
        "LPP_count": int(sys.argv[6]),
        "EP_gradient_threshold": str(sys.argv[7]),
        "LPP_gradients_threshold": str(sys.argv[8]),
        "sell_threshold": str(sys.argv[9]),
        "buy_threshold": str(sys.argv[10]),
        "DIV_PARTS": int(sys.argv[11]),
        "init_last_sell_price": str(sys.argv[12]),
        "init_last_buy_price": str(sys.argv[13])
    }

    log_file = os.path.join(BASE_DIR, "logs", "log", "crypto_trader_bot_%s.log" % trader_parms["pair"])
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    main(trader_parms)
