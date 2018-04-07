import os
import sys
import json
import time
import hmac
import base64
import hashlib
import datetime
import traceback
import logging

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.settings import API_ENDPOINT, API_KEY, API_SECRET

logger = logging.getLogger('crypto_trader_bot')
if len(logger.handlers) == 0:
    ch = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

def try_again_if_failed(repeat_interval):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    result = func(*args, **kwargs)
                    if "error" in result:
                        logger.warning("                                ==================")
                        logger.warning("                                 Try again in %ss " % str(repeat_interval))
                        logger.warning("                                ==================")
                        logger.warning("")
                        time.sleep(repeat_interval)
                        continue
                    else:
                        return result
                except Exception as ex:
                    logger.warning(str(traceback.format_exc()))
                    logger.warning("                                ==================")
                    logger.warning("                                 Try again in %ss " % str(repeat_interval))
                    logger.warning("                                ==================")
                    logger.warning("")
                    time.sleep(repeat_interval)
                    continue

        return wrapper
    return real_decorator

def my_fucking_decoder_for_timestamp(obj):
    if "timestamp" in obj:
        obj["timestamp"] = datetime.datetime.utcfromtimestamp(float(obj["timestamp"])).strftime("%Y-%m-%d %H:%M:%S:%f")
    return obj

def my_fucking_decoder(obj):
    for k,v in obj.items():
        if isinstance(v, list):
            for member in v:
                if isinstance(member, dict):
                    my_fucking_decoder(member)
            continue
        if isinstance(v, dict):
            my_fucking_decoder(v)
            continue

        # try:
        #     obj[k] = int(v)
        #     continue
        # except ValueError:
        #     pass
        try:
            obj[k] = float(v)
        except ValueError:
            pass
    return obj

def show_in_console(data, name):
    t_ = json.dumps(data)
    j_ = json.loads(t_, object_hook=my_fucking_decoder_for_timestamp)
    msg = json.dumps(j_, sort_keys=True, indent=5, separators=(',', ': '))
    # print(Fore.CYAN)
    logger.info("Response: ")
    logger.info("\t" + name + ": \n%s\n" % msg)
    # print(Style.RESET_ALL)
    return None


@try_again_if_failed(repeat_interval=30)
def get_ticker(pair, show_console=False):
    """

        The ticker is a high level overview of the state of the market. 
        It shows you the current best bid and ask, as well as the last trade price. 
        It also includes information such as daily volume and how much the price has moved over the last day.


        Response:

            mid         [price] (bid + ask) / 2
            bid         [price] Innermost bid
            ask         [price] Innermost ask
            last_price  [price] The price at which the last order executed
            low         [price] Lowest trade price of the last 24 hours
            high        [price] Highest trade price of the last 24 hours
            volume      [price] Trading volume of the last 24 hours
            timestamp   [time]  The timestamp at which this information was valid
    """
    req_url = API_ENDPOINT + "/pubticker/" + pair
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Ticker")
    return j

def get_stats(pair, show_console=False):
    """

        Various statistics about the requested pair.


        Response:

            period  [integer]   Period covered in days
            volume  [price]     Volume
    """
    req_url = API_ENDPOINT + "/stats/" + pair
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Stats")
    return j

def get_fundingbook(currency, show_console=False):
    """

        Get the full margin funding book


        Request:

            limit_bids  false   [int]   50  Limit the number of funding bids returned. 
                                            May be 0 in which case the array of bids is empty
            limit_asks  false   [int]   50  Limit the number of funding offers returned. 
                                            May be 0 in which case the array of asks is empty
            
        Response:

            bids        [array of funding bids] 
                rate        [rate in % per 365 days]    
                amount      [decimal]   
                period      [days]          Minimum period for the margin funding contract
                timestamp   [time]  
                frr         [yes/no]        “Yes” if the offer is at Flash Return Rate, 
                                            “No” if the offer is at fixed rate
            asks        [array of funding offers]   
                rate        [rate in % per 365 days]    
                amount      [decimal]   
                period      [days]          Maximum period for the funding contract
                timestamp   [time]  
                frr         [yes/no]        “Yes” if the offer is at Flash Return Rate, 
                                            “No” if the offer is at fixed rate
    """
    req_url = API_ENDPOINT + "/lendbook/" + currency
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Funding book")
    return j

def get_orderbook(pair, show_console=False):
    """

        Get the full order book.


        Request:

            limit_bids  false   [int]   50  Limit the number of bids returned. 
                                            May be 0 in which case the array of bids is empty
            limit_asks  false   [int]   50  Limit the number of asks returned. 
                                            May be 0 in which case the array of asks is empty
            group   false   [0/1]   1   If 1, orders are grouped by price in the orderbook. 
                                            If 0, orders are not grouped and sorted individually
            
        Response:

            bids        [array]
                price       [price]
                amount      [decimal]
                timestamp   [time]
            asks        [array]
                price       [price]
                amount      [decimal]
                timestamp   [time]
    """
    req_url = API_ENDPOINT + "/book/" + pair
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Order book")
    return j

def get_trades(pair, show_console=False):
    """

        Get a list of the most recent trades for the given symbol.


        Request:

            timestamp       false   [time]      Only show trades at or after this timestamp
            limit_trades    false   [int]   50  Limit the number of trades returned. Must be >= 1
        
        Response:

            tid         [integer]   
            timestamp   [time]  
            price       [price] 
            amount      [decimal]   
            exchange    [string]    "bitfinex"
            type        [string]    “sell” or “buy” (can be “” if undetermined)
    """
    req_url = API_ENDPOINT + "/trades/" + pair
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Trades")
    return j

def get_lends(currency, show_console=False):
    """

        Get a list of the most recent funding data for the given currency: 
        total amount provided and Flash Return Rate (in % by 365 days) over time.

        Request Details

            timestamp   false   [time]      Only show data at or after this timestamp
            limit_lends false   [int]   50  Limit the amount of funding data returned. Must be >= 1
            
        Response Details

            rate            [decimal, % by 365 days]    Average rate of total funding received at 
                                                        fixed rates, ie past Flash Return Rate annualized
            amount_lent     [decimal]   Total amount of open margin funding in the given currency
            amount_used     [decimal]   Total amount of open margin funding used in a margin 
                                        position in the given currency
            timestamp       [time]  
    """
    req_url = API_ENDPOINT + "/lends/" + currency
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Lends")
    return j

def get_symbols(show_console=False):
    """

        A list of symbol names.
    """
    req_url = API_ENDPOINT + "/symbols"
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Symbols")
    return j

def get_symbol_details(show_console=False):
    """

        Get a list of valid symbol IDs and the pair details.


        Response:

            pair                [string]    The pair code
            price_precision     [integer]   Maximum number of significant digits for price in this pair
            initial_margin      [decimal]   Initial margin required to open a position in this pair
            minimum_margin      [decimal]   Minimal margin to maintain (in %)
            maximum_order_size  [decimal]   Maximum order size of the pair
            expiration          [string]    Expiration date for limited contracts/pairs
    """
    req_url = API_ENDPOINT + "/symbols_details"
    req = requests.get(req_url)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Symbols details")
    return j




def headers_payload(url, parameters=None):
    nonce = str(int(time.time() * 1000))

    url = "/v1/" + url

    payload = {
        'nonce': nonce,
        'request': url
    }

    logger.info("Request: " + url)
    if parameters is not None:
        logger.info("\tparameters: " + str(parameters))

    if isinstance(parameters, dict):
        payload.update(parameters)

    data = base64.b64encode(json.dumps(payload).encode())

    auth_sig = hmac.new(API_SECRET.encode(), data,
                        hashlib.sha384).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-BFX-APIKEY": API_KEY,
        "X-BFX-PAYLOAD": data,
        "X-BFX-SIGNATURE": auth_sig
    }
    return headers




@try_again_if_failed(repeat_interval=30)
def post_account_info(show_console=False):
    """

        Return information about your account (trading fees)


        Response:

            [{
              "maker_fees":"0.1",
              "taker_fees":"0.2",
              "fees":[{
                "pairs":"BTC",
                "maker_fees":"0.1",
                "taker_fees":"0.2"
               },{
                "pairs":"LTC",
                "maker_fees":"0.1",
                "taker_fees":"0.2"
               },
               {
                "pairs":"ETH",
                "maker_fees":"0.1",
                "taker_fees":"0.2"
              }]
            }]
    """
    rq_url = "account_infos"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Account infos")
    return j

@try_again_if_failed(repeat_interval=30)
def post_account_fees(show_console=False):
    """

        See the fees applied to your withdrawals


        Response:

            {
              "withdraw":{
                "BTC": "0.0005",
                "LTC": 0,
                "ETH": 0,
                ...
              }
            }
    """
    rq_url = "account_fees"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Account fees")
    return j

@try_again_if_failed(repeat_interval=30)
def post_balances(show_console=False):
    """

        See your balances


        Response:

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
    rq_url = "balances"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Balances")
    return j

@try_again_if_failed(repeat_interval=30)
def post_active_orders(show_console=False):
    """

        View your active orders.


        Response:

            [{
              "id":448411365,
              "symbol":"btcusd",
              "exchange":"bitfinex",
              "price":"0.02",
              "avg_execution_price":"0.0",
              "side":"buy",
              "type":"exchange limit",
              "timestamp":"1444276597.0",
              "is_live":true,
              "is_cancelled":false,
              "is_hidden":false,
              "was_forced":false,
              "original_amount":"0.02",
              "remaining_amount":"0.02",
              "executed_amount":"0.0"
            }] 

    """
    rq_url = "orders"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t)#, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Active Orders")
    return j

@try_again_if_failed(repeat_interval=30)
def order(symbol, amount, side, order_type, price=9999999.9, show_console=False):
    """

        return:

            {
                 "avg_execution_price": "0.0",
                 "cid": 84550011275,
                 "cid_date": "2017-11-03",
                 "exchange": "bitfinex",
                 "executed_amount": "0.0",
                 "gid": null,
                 "id": 4844839736,
                 "is_cancelled": false,
                 "is_hidden": false,
                 "is_live": true,
                 "oco_order": null,
                 "order_id": 4844839736,
                 "original_amount": "0.015",
                 "price": "7800.0",
                 "remaining_amount": "0.015",
                 "side": "sell",
                 "src": "api",
                 "symbol": "btcusd",
                 "timestamp": "2017-11-03 23:29:10:073533",
                 "type": "exchange limit",
                 "was_forced": false
            }

    """

    # ocoorder = Set an additional STOP OCO order that will be linked with the current order.
    ocoorder = False


    parameters = {
        "symbol": symbol,
        "amount": format(amount, '.6f'),
        "price": format(price, '.6f'), 
        "side": side, 
        "type": order_type,
        "ocoorder": ocoorder
    }



    rq_url = "order/new"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url, parameters=parameters)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t)#, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="New order: " + side)
    return j

@try_again_if_failed(repeat_interval=30)
def order_status(order_id, show_console=False):
    """

        return:

            {
                 "avg_execution_price": "7119.6",
                 "cid": 171367435,
                 "cid_date": "2017-11-04",
                 "exchange": "bitfinex",
                 "executed_amount": "0.004",
                 "gid": null,
                 "id": 4845411500,
                 "is_cancelled": false,
                 "is_hidden": false,
                 "is_live": false,
                 "oco_order": null,
                 "original_amount": "0.004",
                 "price": "7109.9",
                 "remaining_amount": "0.0",
                 "side": "sell",
                 "src": "api",
                 "symbol": "btcusd",
                 "timestamp": "2017-11-04 00:02:51:000000",
                 "type": "exchange market",
                 "was_forced": false
            }

    """



           # result = "avg_execution_price" * "executed_amount" = 28.4784 - fee 0.2%




    parameters = {
        "order_id": order_id
    }

    rq_url = "order/status"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url, parameters=parameters)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t)#, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Order %s status: " % str(order_id) )
    return j

@try_again_if_failed(repeat_interval=30)
def order_history(limit=None, show_console=False):
    """

        return:

            {
                 "avg_execution_price": "7119.6",
                 "cid": 171367435,
                 "cid_date": "2017-11-04",
                 "exchange": "bitfinex",
                 "executed_amount": "0.004",
                 "gid": null,
                 "id": 4845411500,
                 "is_cancelled": false,
                 "is_hidden": false,
                 "is_live": false,
                 "oco_order": null,
                 "original_amount": "0.004",
                 "price": "7109.9",
                 "remaining_amount": "0.0",
                 "side": "sell",
                 "src": "api",
                 "symbol": "btcusd",
                 "timestamp": "2017-11-04 00:02:51:000000",
                 "type": "exchange market",
                 "was_forced": false
            }

    """



           # result = "avg_execution_price" * "executed_amount" = 28.4784 - fee 0.2%



    if limit is None:
        parameters = None
    else:
        parameters = {
            "limit": limit
        }

    rq_url = "orders/hist"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url, parameters=parameters)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t)#, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Orders history. Limit %s: " % str(limit) )
    return j

@try_again_if_failed(repeat_interval=30)
def trade_history(symbol, since_datetime, until_datetime, show_console=False):
    """

        return:

            [
                 {
                      "amount": "0.004",
                      "fee_amount": "-0.0569568",
                      "fee_currency": "USD",
                      "order_id": 4845411500,
                      "price": "7119.6",
                      "tid": 84998604,
                      "timestamp": "2017-11-04 00:02:51:000000",
                      "type": "Sell"
                 }
            ]


    """

    parameters = {
        "symbol": symbol,
        "timestamp": str(since_datetime.timestamp()),
        "until": str(until_datetime.timestamp())
    }

    rq_url = "mytrades"
    req_url = API_ENDPOINT + "/" + rq_url

    headers = headers_payload(rq_url, parameters=parameters)

    req = requests.post(req_url, headers=headers)
    t = req.text
    j = json.loads(t)#, object_hook=my_fucking_decoder)
    if show_console:
        show_in_console(data=j, name="Trade history from \n%s \nto \n%s: " % (  since_datetime.strftime("%Y-%m-%d %H:%M:%S:%f"),  
            until_datetime.strftime("%Y-%m-%d %H:%M:%S:%f")   ) )
    return j


