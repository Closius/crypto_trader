import os
import json
import signal
from subprocess import Popen, PIPE

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from django.core.exceptions import ObjectDoesNotExist

from management_app.models import Trade, Orders_History, Pair_Timeframe, Candle
from server.settings import BASE_DIR, VIRTUALENV_DIR
from trader.bitfinex_client import post_balances


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def settings():
    work_dir = os.path.join(BASE_DIR, "trader")
    log_dir = os.path.join(BASE_DIR, "logs", "log")
    misc_dir = os.path.join(BASE_DIR, "logs", ".misc")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(misc_dir):
        os.makedirs(misc_dir)

    return work_dir, log_dir, misc_dir

def json_response(data):
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True, indent=5, separators=(',', ': ')), content_type='application/json', status=200)


def run_command_in_virtualenv(command):
    commands = """
    . %s/bin/activate
    %s
    deactivate
    """ % (VIRTUALENV_DIR, command)
    process = Popen(commands, stdout=PIPE, shell=True)
    return process.communicate()


def collector(request):
    """
    .. http:post:: /management/collector/

        Popen(
            ["nohup", 
                    "python3", "/root/crypto_trading/bitfinex/collect_data.py", 
                    ">", "/root/crypto_trading/bitfinex/log/collect_data.out", "&", 
                    "echo", "$!", ">>", "/root/crypto_trading/bitfinex/.misc/collect_data.pid"]
        )

    **Request**:

    .. sourcecode:: json

        {
          "action": "start",  # "stop", "status"
        }

    **Response**:

    .. sourcecode:: json

        {
            "log": "kokokokoko"
        }

        or

        {}


    """
    received_json_data = json.loads(request.body.decode())

    work_dir, log_dir, misc_dir = settings()
    log_file = os.path.join(log_dir, "collect_data.out")
    pid_file = os.path.join(log_dir, "collect_data.pid")
    collector_py = os.path.join(work_dir, "collect_data.py")


    if (received_json_data["action"] == "start") or (received_json_data["action"] == "stop"):
        # Clear
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pids = f.read()
            try:
                os.kill(int(pids), signal.SIGTERM) #or signal.SIGKILL
            except ProcessLookupError:
                pass
            os.remove(pid_file)
        if os.path.exists(log_file):
            os.remove(log_file)

        if received_json_data["action"] == "start":
            command = "nohup python3 " + collector_py + " > " + log_file + " & echo $! >> " + pid_file
            run_command_in_virtualenv(command)

    if received_json_data["action"] == "status":
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pids = f.read()
            pid_is_alive = check_pid(int(pids))
        else:
            pid_is_alive = False

        if os.path.exists(log_file):
            with open(log_file) as f:
                log_text = f.read()
        else:
            log_text = "No log file"

        data = {
            "is_alive": pid_is_alive,
            "log": str(log_text)
        }

        return json_response(data)

    return json_response(dict())

def crypto_trader_bot(request):
    """
    .. http:post:: /management/crypto_trader_bot/

        Start/Stop Crypto tradering bot
                or
        Status of alive Crypto tradering bot

    **Request**:

    .. sourcecode:: json

        {
          "action": "status", # "stop"
          "pair": "XMRUSD"
        }

        or

        {
          "action": "start",
                    "pair": "XMRUSD",
                    "timeframe": "1m",
                    "timeperiod": 9,
                    "init_last_sell_price": 345.3, 
                    "init_last_buy_price": 345.3,
                    "DIV_PARTS": 2, 
                    "LPP_count": 1, 
                    "EP_gradient_threshold": 0.0, 
                    "LPP_gradients_threshold": 0.0, 
                    "sell_threshold": 0.8,
                    "buy_threshold": 0.8,
                    "independent_last_sell_buy_price_checking": false,
                    "forse_commit_sell_buy_status_distace": none
        }

    **Response**:

    .. sourcecode:: json
        
        {
            "log": "kokokokoko"
        }

        or

        {}

    """
    received_json_data = json.loads(request.body.decode())

    work_dir, log_dir, misc_dir = settings()
    out_file = "/dev/null" #os.path.join(log_dir, "trader_%s.out" % received_json_data["pair"])
    log_file = os.path.join(log_dir, "crypto_trader_bot_%s.log" % received_json_data["pair"])
    pid_file = os.path.join(log_dir, "trader_%s.pid" % received_json_data["pair"])
    trader_py = os.path.join(work_dir, "crypto_trader_bot.py")

    if (received_json_data["action"] == "start") or (received_json_data["action"] == "stop"):

        # Clear
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pids = f.read()
            try:
                os.kill(int(pids), signal.SIGTERM) #or signal.SIGKILL
            except ProcessLookupError:
                pass
            os.remove(pid_file)
        if received_json_data["action"] == "start":
            # if os.path.exists(out_file):
            #     os.remove(out_file)
            if os.path.exists(log_file):
                os.remove(log_file)

        if received_json_data["action"] == "start":
            command = "nohup python3 " + trader_py + \
                  " " + str(received_json_data["pair"]) + \
                  " " + str(received_json_data["timeframe"]) + \
                  " " + str(received_json_data["timeperiod"]) + \
                  " " + str(received_json_data["independent_last_sell_buy_price_checking"]) + \
                  " " + str(received_json_data["forse_commit_sell_buy_status_distace"]) + \
                  " " + str(received_json_data["LPP_count"]) + \
                  " " + str(received_json_data["EP_gradient_threshold"]) + \
                  " " + str(received_json_data["LPP_gradients_threshold"]) + \
                  " " + str(received_json_data["sell_threshold"]) + \
                  " " + str(received_json_data["buy_threshold"]) + \
                  " " + str(received_json_data["DIV_PARTS"]) + \
                  " " + str(received_json_data["init_last_sell_price"]) + \
                  " " + str(received_json_data["init_last_buy_price"]) + \
                      " > " + out_file + " & echo $! >> " + pid_file
            run_command_in_virtualenv(command)

    if received_json_data["action"] == "status":
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pids = f.read()
            pid_is_alive = check_pid(int(pids))
        else:
            pid_is_alive = False

        # if os.path.exists(out_file):
        #     with open(out_file) as f:
        #         out_file_text = f.read()
        # else:
        #     out_file_text = "No out file"

        if os.path.exists(log_file):
            with open(log_file) as f:
                log_file_text = f.read()
        else:
            log_file_text = "No log file"

        data = {
            "is_alive": pid_is_alive,
            # "out_file": str(out_file_text),
            "log_file": str(log_file_text)
        }

        return json_response(data)

    return json_response(dict())


def orders_history(request):
    """
    .. http:post:: /management/orders_history/


    **Request**:

    .. sourcecode:: json
        {
          "trade_id": 45,
          "action": "get_all" #, "delete", "get"
        }

    **Response**:

    .. sourcecode:: json

        [
           {}, {}, {}, ...
        ]

    """
    received_json_data = json.loads(request.body.decode())
    trade_id = received_json_data["trade_id"]
    action = received_json_data["action"]

    if action == "get":
        orders_history = Orders_History.objects.filter(trade=trade_id)
        data = list(orders_history.values())
        return json_response(data)
    elif action == "delete":
        Orders_History.objects.filter(trade=trade_id).delete()
        data = list()
        return json_response(data)
    elif action == "get_all":
        orders_history = Orders_History.objects.all()
        data = list(orders_history.values())
        return json_response(data)

def trade(request):
    """
    .. http:post:: /management/trade/

    Delete/Get/Get All

    **Request**:

    .. sourcecode:: json
        {
          "id": 56,
          "action": "get_all" #, "delete", "get"
        }

    **Response**:

    .. sourcecode:: json

        [
           {}, {}, {}, ...
        ]

    """
    received_json_data = json.loads(request.body.decode())
    trade_id = received_json_data["id"]
    action = received_json_data["action"]

    if action == "get":
        trade = Trade.objects.filter(id=trade_id)
        data = list(trade.values())
        return json_response(data)
    elif action == "delete":
        Trade.objects.filter(id=trade_id).delete()
        data = list()
        return json_response(data)
    elif action == "get_all":
        trades = Trade.objects.all()
        all_data = []
        for trade in trades:
            data = model_to_dict(trade)
            BTC_in_the_start = float(trade.initial_BTC_wallet)
            USD_in_the_start = float(trade.initial_USD_wallet)
            pair = trade.pair_timeframe.pair
            timeframe = trade.pair_timeframe.timeframe
            try:
                orders_history_count = Orders_History.objects.filter(trade=trade).count()
                orders_history_last = Orders_History.objects.filter(trade=trade).latest('mts')
                BTC_in_the_end = sum(orders_history_last.misc['BTC'])
                USD_in_the_end = sum(orders_history_last.misc['USD'])
                data.update({
                    "orders_history_count": orders_history_count,
                    "profit_BTC": str(BTC_in_the_start) + " --> " + str(BTC_in_the_end),
                    "profit_USD": str(USD_in_the_start) + " --> " + str(USD_in_the_end),
                    "pair": pair,
                    "timeframe": timeframe
                })
            except ObjectDoesNotExist:
                data.update({
                    "orders_history_count": 0,
                    "profit_BTC": str(BTC_in_the_start) + " --> N/A",
                    "profit_USD": str(USD_in_the_start) + " --> N/A",
                    "pair": pair,
                    "timeframe": timeframe
                })

            all_data.append(data)

        return json_response(all_data)

def pairs(request):
    """
    .. http:post:: /management/pairs/

        Create/Delete/Get/Get All

    **Request**:

    .. sourcecode:: json
        {
          "pair": "XMRUSD",
          "timeframe": "1m",
          "action": "get_all" #, "delete", "get", "put"
        }

    **Response**:

    .. sourcecode:: json

        "put":
        [
           23
        ]

        "get":
        [
           23
        ]

        "get_all":
        [
             {
                  "id": 1,
                  "pair": "XMRUSD",
                  "timeframe": "1m"
             },
             {
                  "id": 4,
                  "pair": "XMRUSD",
                  "timeframe": "5m"
             },
             {
                  "id": 6,
                  "pair": "XMRUSD",
                  "timeframe": "15m"
             }
        ]

        "delete":
        []

    """
    received_json_data = json.loads(request.body.decode())
    pair = received_json_data["pair"]
    timeframe = received_json_data["timeframe"]
    action = received_json_data["action"]

    if action == "get":
        pair_timeframe = Pair_Timeframe.objects.get(pair=pair, timeframe=timeframe)
        data = [pair_timeframe.id]
        return json_response(data)
    elif action == "put":
        pair_timeframe = Pair_Timeframe(pair=pair, timeframe=timeframe)
        pair_timeframe.save()
        data = [pair_timeframe.id]
        return json_response(data)
    elif action == "delete":
        Pair_Timeframe.objects.filter(pair=pair, timeframe=timeframe).delete()
        data = list()
        return json_response(data)
    elif action == "get_all":
        pair_timeframe = Pair_Timeframe.objects.all()
        if pair_timeframe.count() == 0:
            return json_response([])
        else:
            data = list(pair_timeframe.values())
            return json_response(data)

def candles(request):
    """
    .. http:post:: /management/candles/

        Create/Delete/Get/Get All/Delete All/Count

    **Request**:

    .. sourcecode:: json
        {
          "pair": "XMRUSD",
          "timeframe": "1m",
          "action": "get" #, "delete", "delete_all", "count"
        }

    **Response**:

    .. sourcecode:: json

        "get":
        [
             {
                  "close": "272.4500000000000000000000000000000000000000",
                  "high": "274.3400000000000000000000000000000000000000",
                  "id": 419,
                  "low": "272.4500000000000000000000000000000000000000",
                  "mts": "2018-03-08T22:50:00Z",
                  "open": "274.3300000000000000000000000000000000000000",
                  "pair_timeframe_id": 4,
                  "volume": "447.7072914500000000000000000000000000000000"
             },
             {
                  "close": "274.2100000000000000000000000000000000000000",
                  "high": "276.6500000000000000000000000000000000000000",
                  "id": 420,
                  "low": "273.1700000000000000000000000000000000000000",
                  "mts": "2018-03-08T22:55:00Z",
                  "open": "275.2600000000000000000000000000000000000000",
                  "pair_timeframe_id": 4,
                  "volume": "1032.2220301600000000000000000000000000000000"
             },
             ...
         ]


        "delete":
        []

    """

    received_json_data = json.loads(request.body.decode())
    action = received_json_data["action"]
    if action != "delete_all":
        pair = received_json_data["pair"]
        timeframe = received_json_data["timeframe"]

    if action == "get":
        candles = Candle.objects.filter(pair_timeframe__pair=pair, pair_timeframe__timeframe=timeframe)
        data = list(candles.order_by('-mts').values())
        return json_response(data)
    elif action == "delete":
        Candle.objects.filter(pair_timeframe__pair=pair, pair_timeframe__timeframe=timeframe).delete()
        data = list()
        return json_response(data)
    elif action == "delete_all":
        Candle.objects.all().delete()
    elif action == "count":
        if (pair != "") and (timeframe != ""):
            pairs_timeframes = Pair_Timeframe.objects.filter(pair=pair, timeframe=timeframe).values()
        else:
            pairs_timeframes = Pair_Timeframe.objects.all().values()
        data = []
        for pair_timeframe in pairs_timeframes:
            pair = pair_timeframe["pair"]
            timeframe = pair_timeframe["timeframe"]
            pair_timeframe_id = pair_timeframe["id"]
            count = Candle.objects.filter(pair_timeframe_id=pair_timeframe_id).count()
            last = Candle.objects.filter(pair_timeframe_id=pair_timeframe_id).latest('mts')
            data.append({
                "pair": pair,
                "timeframe": timeframe,
                "count": count,
                "last": {
                    "id": last.id,
                    "mts": last.mts,
                    "open": float(last.open),
                    "close": float(last.close),
                    "low": float(last.low),
                    "high": float(last.high),
                    "volume": float(last.volume)
                }
            })
        data = sorted(data, key=lambda x: x["timeframe"])
        return json_response(data)
    return json_response([])


def balance(request):
    """
    .. http:post:: /management/balance/



    **Request**:

    .. sourcecode:: json

    **Response**:

    .. sourcecode:: json

            [{
              "type":"deposit",
              "currency":"btc",
              "amount":"0.0",
              "available":"0.0"
            },{
              "type":"deposit",
              "currency":"usd",
              "amount":"1.0",
              "available":"1.0"
            },
            ...]

    """

    r = post_balances()

    return json_response(r)


