import logging
import sys
import math

import numpy as np
import talib

logger = logging.getLogger('crypto_trader_bot')
if len(logger.handlers) == 0:
    ch = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

def show_settings(
    pair,
    independent_last_sell_buy,
    forse_commit_sell_buy_status_distace,
    timeframe,
    timeperiod_TEMA,
    LPP_count,
    EP_gradient_threshold,
    LPP_gradients_threshold,
    sell_threshold,
    buy_threshold,
    init_last_sell_price,
    init_last_buy_price,
    initial_BTC_wallet,
    initial_USD_wallet,
    DIV_PARTS,
    start_trading,
    end_trading=None):

    logger.info('''
     #_                                                                       d
     ##_                                                                     d#
     NN#p                                                                  j0NN
     40NNh_                                                              _gN#B0
     4JF@NNp_                                                          _g0WNNL@
     JLE5@WRNp_                                                      _g@NNNF3_L
     _F`@q4WBN@Np_                                                _gNN@ZL#p"Fj_
     "0^#-LJ_9"NNNMp__                                         _gN#@#"R_#g@q^9"
     a0,3_j_j_9FN@N@0NMp__                                __ggNZNrNM"P_f_f_E,0a
      j  L 6 9""Q"#^q@NDNNNMpg____                ____gggNNW#W4p^p@jF"P"]"j  F
     rNrr4r*pr4r@grNr@q@Ng@q@N0@N#@NNMpmggggmqgNN@NN@#@4p*@M@p4qp@w@m@Mq@r#rq@r
       F Jp 9__b__M,Juw*w*^#^9#""EED*dP_@EZ@^E@*#EjP"5M"gM@p*Ww&,jL_J__f  F j
     -r#^^0""E" 6  q  q__hg-@4""*,_Z*q_"^pwr""p*C__@""0N-qdL_p" p  J" 3""5^^0r-
       t  J  __,Jb--N""",  *_s0M`""q_a@NW__JP^u_p"""p4a,p" _F""V--wL,_F_ F  #
     _,Jp*^#""9   L  5_a*N"""q__INr" "q_e^"*,p^""qME_ y"""p6u,f  j'  f "N^--LL_
        L  ]   k,w@#"""_  "_a*^E   ba-" ^qj-""^pe"  J^-u_f  _f "q@w,j   f  jL
        #_,J@^""p  `_ _jp-""q  _Dw^" ^cj*""*,j^  "p#_  y""^wE_ _F   F"^qN,_j
     w*^0   4   9__sAF" `L  _Dr"  m__m""q__a^"m__*  "qA_  j" ""Au__f   J   0^--
        ]   J_,x-E   3_  jN^" `u _w^*_  _RR_  _J^w_ j"  "pL_  f   7^-L_F   #
        jLs*^6   `_  _&*"  q  _,NF   "wp"  "*g"   _NL_  p  "-d_   F   ]"*u_F
     ,x-"F   ]    Ax^" q    hp"  `u jM""u  a^ ^, j"  "*g_   p  ^mg_   D.H. 1992
     ''')

    logger.info("")
    logger.info("")
    logger.info("==========================================")
    logger.info("============================================")
    logger.info("==============================================")
    logger.info("================================================")
    logger.info("==================================================")
    logger.info("====================================================")
    logger.info("======================================================")
    logger.info("========================================================")
    logger.info("==========================================================")
    logger.info("============================================================")
    logger.info("==============================================================")
    logger.info("================================================================")
    logger.info("==================================================================")
    logger.info("====================================================================")
    logger.info("                     Strategy parameters:")
    logger.info("      start trading datetime (UTC, 24h): " + start_trading.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("")
    logger.info("Pair: " + pair)
    logger.info("timeframe (minutes): " + str(timeframe))
    logger.info("timeperiod (TEMA): " + str(timeperiod_TEMA))
    logger.info("init_last_buy_price: " + str(init_last_buy_price))
    logger.info("init_last_sell_price: " + str(init_last_sell_price))
    logger.info("initial_BTC_wallet: " + str(initial_BTC_wallet))
    logger.info("initial_USD_wallet: " + str(initial_USD_wallet))
    logger.info("Wallet parts: " + str(DIV_PARTS))
    logger.info("---")
    logger.info("Independent last sell buy price checking: " + str(independent_last_sell_buy))
    logger.info("Forse commit sell<->buy by distace: " + str(forse_commit_sell_buy_status_distace))
    if str(forse_commit_sell_buy_status_distace) != "None":
        logger.info("""            Warning!
                This operation can be repeated more than one time. Therefore, 
                last_sell_buy_distace[index]["loss"] will be extended by adding the current loss value
                It may have an effect like a snowslip and the operation will be never performed!""")

    logger.info("LPP_count: " + str(LPP_count))
    logger.info("EP_gradient_threshold: " + str(EP_gradient_threshold))
    logger.info("LPP_gradients_threshold: " + str(LPP_gradients_threshold))
    logger.info("---")
    logger.info("                 Min desired profit (%):")
    logger.info("        (real profit will be probably less because of ")
    logger.info("   amount remains after order execution, amount calculation ")
    logger.info("         for Sell/Buy order request, rounding etc)")
    logger.info("(MSP) Sell: " + str(sell_threshold))
    logger.info("(MBP) Buy: " + str(buy_threshold))
    if end_trading is not None:
        logger.info("---")
        logger.info("end trading (statistic) datetime (UTC): " + end_trading.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("====================================================================")
    logger.info("==================================================================")
    logger.info("=== Anton Kavalerov, 2017 ======================================")
    logger.info("==============================================================")
    logger.info("============================================================")
    logger.info("==========================================================")
    logger.info("========================================================")
    logger.info("======================================================")
    logger.info("====================================================")
    logger.info("==================================================")
    logger.info("================================================")
    logger.info("==============================================")
    logger.info("============================================")
    logger.info("==========================================")

    logger.info('''
                          __gggrgM**M#mggg__
                     __wgNN@"B*P""mp""@d#"@N#Nw__
                   _g#@0F_a*F#  _*F9m_ ,F9*__9NG#g_
                _mN#F  aM"    #p"    !q@    9NL "9#Qu_
               g#MF _pP"L  _g@"9L_  _g""#__  g"9w_ 0N#p
             _0F jL*"   7_wF     #_gF     9gjF   "bJ  9h_
            j#  gAF    _@NL     _g@#_      J@u_    2#_  #_
           ,FF_#" 9_ _#"  "b_  g@   "hg  _#"  !q_ jF "*_09_
           F N"    #p"      Ng@       `#g"      "w@    "# t
          j p#    g"9_     g@"9_      gP"#_     gF"q    Pb L
          0J  k _@   9g_ j#"   "b_  j#"   "b_ _d"   q_ g  ##
          #F  `NF     "#g"       "Md"       5N#      9W"  j#
          #k  jFb_    g@"q_     _*"9m_     _*"R_    _#Np  J#
          tApjF  9g  J"   9M_ _m"    9%_ _*"   "#  gF  9_jNF
           k`N    "q#       9g@        #gF       ##"    #"j
           `_0q_   #"q_    _&"9p_    _g"`L_    _*"#   jAF,'
            9# "b_j   "b_ g"    *g _gF    9_ g#"  "L_*"qNF
             "b_ "#_    "NL      _B#      _I@     j#" _#"
               NM_0"*g_ j""9u_  gP  q_  _w@ ]_ _g*"F_g@
                "NNh_ !w#_   9#g"    "m*"   _#*" _dN@"
                   9##g_0@q__ #"4_  j*"k __*NF_g#@P"
                     "9NN#gIPNL_ "b@" _2M"Lg#N@F"
                         ""P@*NN#gEZgNN@#@P""
    ''')
    logger.info("")
    logger.info("")

def order_inform(original_amount, average_price, count_of_orders_parts, remains_BTC, fee_amount, fee_currency, 
    divided_USD_wallet_current, divided_BTC_wallet_current, date, type_, index, last_buy_price, last_sell_price):


    logger.info("====================================================================")
    if type_ == "SELL":
        logger.info('''

                                 ==============
                                 \            /
                                  \   SELL   /
                                   \        /
                                    \      /
                                     \    /
                                      \  / 
            ''')
    elif type_ == "BUY":
        logger.info('''

                                       / \\
                                      /   \\
                                     /     \\
                                    /       \\
                                   /   BUY   \\
                                  /           \\
                                  =============   
            ''')
    logger.info("Date (UTC): " + date[-1].strftime("%Y-%m-%d %H:%M:%S:%f"))
    logger.info("Wallet index: " + str(index))
    logger.info("")
    logger.info("Average price (USD): " + str(average_price))
    logger.info("Original amount (BTC): " + str(original_amount))
    logger.info("")
    logger.info("                           Execution order info:")
    logger.info("Count of order's parts: " + str(count_of_orders_parts))
    logger.info("remaining BTC: " + str(remains_BTC))
    logger.info("                                    Fee:")
    logger.info("Amount: " + str(fee_amount))
    logger.info("Currency: " + str(fee_currency))
    logger.info("")
    logger.info("")
    logger.info("                         Current divided weallets:")
    logger.info("USD: " + str(divided_USD_wallet_current))
    logger.info("BTC: " + str(divided_BTC_wallet_current))
    logger.info("")
    logger.info("                Last (including current operation) prices:")
    logger.info("sell: " + str(last_sell_price))
    logger.info("buy: " + str(last_buy_price))
    logger.info('''====================================================================



    ''')

class Strategy():
    def __init__(self, date, 
        init_last_sell_price, init_last_buy_price,
        initial_BTC_wallet, initial_USD_wallet, DIV_PARTS=3, timeperiod_TEMA=9, verbose=False,
        LPP_count=5, EP_gradient_threshold=0, LPP_gradients_threshold=0, sell_threshold=0.2, buy_threshold=0.2, production=False, 
        independent_last_sell_buy=True, forse_commit_sell_buy_status_distace=None, pair="BTCUSD", trade_id=None):

        self.last_datetime = date[-1]

        self.production = production

        self.pair = pair.upper()

        self.sell_threshold = sell_threshold
        self.buy_threshold = buy_threshold

        self.LPP_count = LPP_count
        self.EP_gradient_threshold = EP_gradient_threshold
        self.LPP_gradients_threshold = LPP_gradients_threshold

        self.DIV_PARTS = DIV_PARTS

        self.forse_commit_sell_buy_status_distace = forse_commit_sell_buy_status_distace

        if self.forse_commit_sell_buy_status_distace is not None:
            self.last_sell_buy_distace = []
            for i in range(self.DIV_PARTS):
                self.last_sell_buy_distace.append({"last_operation_current_distance": 0,
                                                   "loss": 0.0})

        self.date = date

        # minutes
        self.timeframe = (self.date[1] - self.date[0]).seconds / 60

        self.independent_last_sell_buy = independent_last_sell_buy

        self.last_sell_price = self.get_divided(init_last_sell_price, self.DIV_PARTS)     
        self.last_buy_price = self.get_divided(init_last_buy_price, self.DIV_PARTS)   

        self.timeperiod_TEMA = timeperiod_TEMA

        self.divided_BTC_wallet_current = self.get_divided_wallet(initial_BTC_wallet, self.DIV_PARTS)
        self.divided_USD_wallet_current = self.get_divided_wallet(initial_USD_wallet, self.DIV_PARTS)

        self.orders_history = []

        self.verbose = verbose

        if self.verbose:
            show_settings(
                pair=self.pair,
                independent_last_sell_buy=self.independent_last_sell_buy,
                forse_commit_sell_buy_status_distace=self.forse_commit_sell_buy_status_distace,
                timeframe=self.timeframe,
                timeperiod_TEMA=self.timeperiod_TEMA,
                LPP_count=self.LPP_count,
                EP_gradient_threshold=self.EP_gradient_threshold,
                LPP_gradients_threshold=self.LPP_gradients_threshold,
                sell_threshold=self.sell_threshold,
                buy_threshold=self.buy_threshold,
                init_last_sell_price=init_last_sell_price,
                init_last_buy_price=init_last_buy_price,
                initial_BTC_wallet=initial_BTC_wallet,
                initial_USD_wallet=initial_USD_wallet,
                DIV_PARTS=self.DIV_PARTS,
                start_trading=self.last_datetime,
                end_trading=self.date[-1])

        if self.production:
            self.trade_id = trade_id


    def get_divided(self, amount, parts):
        divided = []
        for i in range(parts):
            divided.append(amount)
        return divided

    def get_divided_wallet(self, amount, parts):
        divided_wallet_current = []
        for i in range(parts):
            divided_wallet_current.append(amount/parts)
        return divided_wallet_current

    def do_operation(self, type_, index, current_best_ask, current_best_bid, fee, calc_last_sell_buy_distace_loss=False):
        """
            Run order section
        """

        if type_ == "SELL":


            # SELL ON THE STOCK EXCHANGE
            req = self.sell(pair=self.pair, amount=self.divided_BTC_wallet_current[index], price=current_best_ask, fee=fee, 
                divided_BTC_wallet_current=self.divided_BTC_wallet_current, divided_USD_wallet_current=self.divided_USD_wallet_current, index=index)
            if req is None:
                return None

            price, BTC_init, USD_init, USD_end, BTC_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current = req

            if self.forse_commit_sell_buy_status_distace is not None:
                if calc_last_sell_buy_distace_loss:
                    self.last_sell_buy_distace[index]["loss"] += math.fabs(self.sell_buy_threshold - math.fabs(price - self.last_buy_price[index]))
                else:
                    self.last_sell_buy_distace[index]["loss"] = 0.0

            if self.independent_last_sell_buy:
                for i in range(self.DIV_PARTS):
                    self.last_sell_price[i] = price
            else: 
                self.last_sell_price[index] = price    

            current_date = self.date[-1]

            self.divided_USD_wallet_current = divided_USD_wallet_current
            self.divided_BTC_wallet_current = divided_BTC_wallet_current

            # self.divided_BTC_wallet_current[index] = BTC_end
            # self.divided_USD_wallet_current[index] += USD_end

            self.orders_history.append({
                "mts": current_date,
                "type": "sell",
                "price": price,
                "amount": BTC_init,

                "usd_init_in_wallet": USD_init,
                "btc_init_in_wallet": BTC_init,

                "usd_end_in_wallet": USD_end,
                "btc_end_in_wallet": BTC_end,

                "index": index,
                "loss": 0.0 if self.forse_commit_sell_buy_status_distace is None else self.last_sell_buy_distace[index]["loss"],
                "fee_currency": fee_currency,
                "fee_amount": fee_amount

            })

            # INSERT DB
            if self.production:
                m = {
                    'USD' : self.divided_USD_wallet_current,
                    'BTC' : self.divided_BTC_wallet_current
                }
                self.insert_trader_db(
                    trade_id=self.trade_id,
                    mts=current_date, 
                    wallet_index=index, 
                    price=price, 
                    amount=BTC_init,

                    usd_init_in_wallet=USD_init,
                    btc_init_in_wallet=BTC_init,
                    usd_end_in_wallet=USD_end,
                    btc_end_in_wallet=BTC_end,

                    fee_amount=fee_amount,
                    fee_currency=fee_currency,
                    loss= 0.0 if self.forse_commit_sell_buy_status_distace is None else self.last_sell_buy_distace[index]["loss"],
                    misc= m,
                    pair=self.pair,
                    kind="sell"
                )

            if self.verbose:
                order_inform(original_amount=BTC_init, average_price=price, count_of_orders_parts=count_of_orders_parts, 
                    remains_BTC=BTC_end, fee_amount=fee_amount, fee_currency=fee_currency,
                    divided_USD_wallet_current=self.divided_USD_wallet_current, divided_BTC_wallet_current=self.divided_BTC_wallet_current, date=self.date, type_=type_,
                    index=index, last_buy_price=self.last_buy_price, last_sell_price=self.last_sell_price)
            return None


        elif type_ == "BUY":

            # BUY ON THE STOCK EXCHANGE
            req = self.buy(pair=self.pair, how_much_usd_I_want_spend_for_buy=self.divided_USD_wallet_current[index], price=current_best_bid, fee=fee,
                divided_BTC_wallet_current=self.divided_BTC_wallet_current, divided_USD_wallet_current=self.divided_USD_wallet_current, index=index)
            if req is None:
                return None

            price, BTC_init, USD_init, USD_end, BTC_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current = req

            if self.forse_commit_sell_buy_status_distace is not None:
                if calc_last_sell_buy_distace_loss:
                    self.last_sell_buy_distace[index]["loss"] += math.fabs(self.sell_buy_threshold - math.fabs(price - self.last_sell_price[index]))
                else:
                    self.last_sell_buy_distace[index]["loss"] = 0.0

            if self.independent_last_sell_buy:
                for i in range(self.DIV_PARTS):
                    self.last_buy_price[i] = price
            else: 
                self.last_buy_price[index] = price    

            current_date = self.date[-1]

            self.divided_USD_wallet_current = divided_USD_wallet_current
            self.divided_BTC_wallet_current = divided_BTC_wallet_current

            # self.divided_USD_wallet_current[index] = USD_end
            # self.divided_BTC_wallet_current[index] += BTC_end

            self.orders_history.append({
                "mts": current_date,
                "type": "buy",
                "price": price,
                "amount": BTC_init,

                "usd_init_in_wallet": USD_init,
                "btc_init_in_wallet": BTC_init,

                "usd_end_in_wallet": USD_end,
                "btc_end_in_wallet": BTC_end,

                "index": index,
                "loss": 0.0 if self.forse_commit_sell_buy_status_distace is None else self.last_sell_buy_distace[index]["loss"],
                "fee_currency": fee_currency,
                "fee_amount": fee_amount
            })


            # INSERT DB
            if self.production:
                m = {
                    'USD' : self.divided_USD_wallet_current,
                    'BTC' : self.divided_BTC_wallet_current
                }
                self.insert_trader_db(
                    trade_id=self.trade_id,
                    mts=current_date, 
                    wallet_index=index, 
                    price=price, 
                    amount=BTC_init,

                    usd_init_in_wallet=USD_init,
                    btc_init_in_wallet=BTC_init,
                    usd_end_in_wallet=USD_end,
                    btc_end_in_wallet=BTC_end,

                    fee_amount=fee_amount,
                    fee_currency=fee_currency,
                    loss= 0.0 if self.forse_commit_sell_buy_status_distace is None else self.last_sell_buy_distace[index]["loss"],
                    misc= m,
                    pair=self.pair,
                    kind="buy"
                )

            if self.verbose:
                order_inform(original_amount=BTC_init, average_price=price, count_of_orders_parts=count_of_orders_parts, 
                    remains_BTC=BTC_end, fee_amount=fee_amount, fee_currency=fee_currency,
                    divided_USD_wallet_current=self.divided_USD_wallet_current, divided_BTC_wallet_current=self.divided_BTC_wallet_current, date=self.date, type_=type_,
                    index=index, last_buy_price=self.last_buy_price, last_sell_price=self.last_sell_price)
            return None

    def sell(self, pair, amount, price, fee, divided_BTC_wallet_current, divided_USD_wallet_current, index):
        """
            Sell on stock exchange

            fee USD in parts (not %)

            usd_got musht be calculated by stock exchange wallet amount and divided_USD_wallet_current

            Returns corrected divided_BTC_wallet_current, divided_USD_wallet_current 

            Must be overridden in production!
        """
        usd_got = (amount * price) * (1 - fee)
        fee_amount = usd_got - (amount * price)
        fee_currency = "USD"
        count_of_orders_parts=1 # how many orders was done for current operation

        USD_init = divided_USD_wallet_current[index]
        BTC_init = divided_BTC_wallet_current[index]

        USD_end = usd_got   #remaining_amount_USD
        BTC_end = 0.0       #remaining_amount_BTC

        # Wallets correction
        divided_USD_wallet_current[index] = USD_end
        divided_BTC_wallet_current[index] = BTC_end

        return price, BTC_init, USD_init, USD_end, BTC_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current

    def buy(self, pair, how_much_usd_I_want_spend_for_buy, price, fee, divided_BTC_wallet_current, divided_USD_wallet_current, index):
        """
            Buy on stock exchange

            fee USD in parts (not %)

            btc_got musht be calculated by stock exchange wallet amount and divided_BTC_wallet_current

            Returns corrected divided_BTC_wallet_current, divided_USD_wallet_current 

            Must be overridden in production!
        """
        btc_got = ((how_much_usd_I_want_spend_for_buy * (1 - fee) ) / price)
        fee_amount = btc_got - (how_much_usd_I_want_spend_for_buy / price)
        fee_currency = "BTC"
        count_of_orders_parts=1

        USD_init = how_much_usd_I_want_spend_for_buy # should be equal to divided_USD_wallet_current[index]
        BTC_init = divided_BTC_wallet_current[index]

        USD_end = 0.0       #remaining_amount_USD
        BTC_end = btc_got   #remaining_amount_BTC

        # Wallets correction
        divided_USD_wallet_current[index] = USD_end
        divided_BTC_wallet_current[index] = BTC_end

        return price, BTC_init, USD_init, USD_end, BTC_end, fee_amount, fee_currency, count_of_orders_parts, divided_BTC_wallet_current, divided_USD_wallet_current

    def insert_trader_db(self, trade_id, mts, wallet_index, price, amount, usd_init_in_wallet, btc_init_in_wallet, 
        usd_end_in_wallet, btc_end_in_wallet, fee_amount, fee_currency, loss, misc, pair, kind):
        """
            Insert in DB

            Must be overridden in production!
        """
        pass

    def calculate(self, last_N_candle_prices, las_N_current_date,
        maker_fee, taker_fee,
        current_best_ask, current_best_bid):

        # REPEAT checking for production. If there is no changes  
        # before: ["9:05", "9:06", "9:07", "9:08"]
        # now:    ["9:05", "9:06", "9:07", "9:08"]
        if las_N_current_date[-1] == self.last_datetime:
            return None
        else:
            self.last_datetime = las_N_current_date[-1]

        self.date = las_N_current_date
        candle_prices_TEMA = talib.TEMA(last_N_candle_prices, timeperiod=self.timeperiod_TEMA)

        # We can't trust the last value because it is currenly vary

        count_of_TEMA = len(candle_prices_TEMA)
        # MOOVING AVERAGE
        window_3 = 3
        last_3_steps_MA1 = candle_prices_TEMA[count_of_TEMA - window_3 - 1: count_of_TEMA - 1]
        window_5 = window_3 + self.LPP_count
        before_last_3_steps_MA1 = candle_prices_TEMA[count_of_TEMA - window_5 - 1: count_of_TEMA - (window_3 - 1) - 1]

        # GRADIENTS CALCULATION
        grad_5 = np.gradient(before_last_3_steps_MA1)
        #                               -                                                     +
        grad_before_down = all(grad_5[i] < self.LPP_gradients_threshold for i in range(len(grad_5)))
        grad_before_up = all(grad_5[i] > self.LPP_gradients_threshold for i in range(len(grad_5)))
        grad = np.gradient(last_3_steps_MA1)
        left_gradient = grad[0]
        middle_gradient = grad[1]
        right_current_gradient = grad[-1]


        if self.verbose and self.production:
            logger.info("{=}  Current checking datetime (UTC): " + self.last_datetime.strftime("%Y-%m-%d %H:%M:%S") )
            logger.info("{=}  TEMA (Candle price) from DB: " + str(candle_prices_TEMA[-1]))
            logger.info("{=}  Current best ASK from DB: " + str(current_best_ask))
            logger.info("{=}  Current best BID from DB: " + str(current_best_bid))
            logger.info("{=}                Fee:")
            logger.info("{=}  Maker fee: " + str(maker_fee) + " %")
            logger.info("{=}  Taker fee: " + str(taker_fee) + " %")
            logger.info("{=}                Profit limit:")
            logger.info("{=}  min profit sell: " + str(self.sell_threshold) + " %")
            logger.info("{=}  min profit buy: " + str(self.buy_threshold) + " %")
            logger.info("{=}                Current percentage from last order price:")
            p = []
            for index in range(self.DIV_PARTS):
                if self.divided_BTC_wallet_current[index] > 0.0:
                    init = self.last_buy_price[index]
                    curr = current_best_ask
                else:
                    init = self.last_sell_price[index]
                    curr = current_best_bid
                p.append(  ((curr - init) /  init ) * 100  )
            logger.info("{=}  " + str(p) + " %")
            logger.info("{=}  ")
            logger.info("{=}                Wallets:")
            logger.info("{=}  BTC: " + str(self.divided_BTC_wallet_current))
            logger.info("{=}  USD: " + str(self.divided_USD_wallet_current))
            logger.info("{=}  ")
            logger.info("{=}                Last sell/buy price:")
            logger.info("{=}  SELL: " + str(self.last_sell_price))
            logger.info("{=}  BUY: " + str(self.last_buy_price))
            logger.info("{=}  ")
            logger.info("{=}                Waiting for:")
            wf = []
            for index in range(self.DIV_PARTS):
                wf.append("")
                if self.divided_BTC_wallet_current[index] > 0.0:
                    wf[index] += "SELL"
                if self.divided_USD_wallet_current[index] > 0.0:
                    wf[index] += "BUY"
            logger.info("{=}  " + str(wf))

        min_profit_sell = self.sell_threshold / 100
        min_profit_buy = self.buy_threshold / 100
        maker_fee = maker_fee / 100
        taker_fee = taker_fee / 100




        # =====================================================================================================================================
        #
        #                                             Forse commit "sell<->buy" by distace
        #
        # =====================================================================================================================================

        # Warning!
        # This operation can be repeated more than one time. Therefore, 
        # self.last_sell_buy_distace[index]["loss"] will be extended by adding the current loss value
        # It may have an effect like a snowslip and the operation will be never performed!


        # =====================================================================================================================================
        #
        #                                                      S E L L
        #
        # =====================================================================================================================================
        break_loop = False
        if (left_gradient > self.EP_gradient_threshold) and (right_current_gradient < self.EP_gradient_threshold) and (grad_before_up is True):
            for index in range(self.DIV_PARTS):
            # for index in reversed(range(len(self.divided_BTC_wallet_current))):
                if self.divided_BTC_wallet_current[index] > 0.0:

                    init = self.last_buy_price[index]
                    curr = current_best_ask
                    p = (curr - init) /  init

                    # TODO:
                    # should wait in the current timeframe inerval 
                    # maybe next value will be better

                    # Note:
                    # If you change order type - check fee's type: TAKER or MAKER

                    if (not break_loop) and (p > (taker_fee + min_profit_sell) ) :
                        self.do_operation(type_="SELL", index=index, current_best_ask=current_best_ask, current_best_bid=current_best_bid, fee=taker_fee)
                        if self.forse_commit_sell_buy_status_distace is not None:
                            self.last_sell_buy_distace[index]["last_operation_current_distance"] = 0
                        # break
                        break_loop = True

        # =====================================================================================================================================
        #
        #                                                      B U Y
        #
        # =====================================================================================================================================    
        break_loop = False
        if (left_gradient < self.EP_gradient_threshold) and (right_current_gradient > self.EP_gradient_threshold) and  (grad_before_down is True):
            for index in range(self.DIV_PARTS):
                if self.divided_USD_wallet_current[index] > 0.0:

                    init = current_best_bid
                    curr = self.last_sell_price[index] 
                    p = (curr - init) /  init

                    # TODO:
                    # should wait in the current timeframe inerval 
                    # maybe next value will be better

                    # Note:
                    # If you change order type - check fee's type: TAKER or MAKER

                    if (not break_loop) and (p > (taker_fee + min_profit_buy)):
                        self.do_operation(type_="BUY", index=index, current_best_ask=current_best_ask, current_best_bid=current_best_bid, fee=taker_fee)
                        if self.forse_commit_sell_buy_status_distace is not None:
                            self.last_sell_buy_distace[index]["last_operation_current_distance"] = 0
                        # break
                        break_loop = True
