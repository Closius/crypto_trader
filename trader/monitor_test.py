import sys
import os
application_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(application_dir)
import json
import datetime
import itertools

import matplotlib.pyplot as plt
import statsmodels.api as sm
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
import talib

import strategy as st
import monitor_test_misc



class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = monitor_test_misc.Ui_Form()
        self.ui.setupUi_over(self)

        self.ui.fetch_data_button.clicked.connect(self.fetch_data)
        self.ui.test_strategy_button.clicked.connect(self.test_strategy)
        self.ui.ts_analysis_button.clicked.connect(self.ts_analysis)
        self.ui.show_real_button.clicked.connect(self.show_real)
        self.ui.investigate_button.clicked.connect(self.investigate_strategy)
        self.ui.get_existing_real_trades_button.clicked.connect(self.get_trades)

    def closeEvent(self, event):
        self.run_timer = False

    def fetch_data(self, event=None, verbose=True, 
        timeframe=None,
        timeperiod=None,
        window_fetch=None,
        pair=None):

        if verbose:
            self.ui.clear(parts=["top", "strategy"])

            self.ui.test_strategy_button.setEnabled(True)
            self.ui.ts_analysis_button.setEnabled(True)
            self.ui.existing_real_trades.setEnabled(False)
            self.ui.show_real_button.setEnabled(False)
            self.ui.get_existing_real_trades_button.setEnabled(True)
            self.ui.slider_begin.setEnabled(True)
            self.ui.slider_end.setEnabled(True)
            self.ui.range_begin_dt.setEnabled(True)
            self.ui.range_end_dt.setEnabled(True)
            self.ui.clear_main_plot_button.setEnabled(True)
            self.ui.investigate_button.setEnabled(True)

        self.window_fetch = 100 if window_fetch is None else window_fetch

        timeframe = self.ui.timeframe_test.currentText() if timeframe is None else timeframe

        timeperiod = int(self.ui.timeperiod_test.value()) if timeperiod is None else timeperiod
        pair = self.ui.pair_test.currentText() if pair is None else pair

        date, openp, closep, highp, lowp, volumep = monitor_test_misc.fetch_candles(pair, timeframe)

        first_not_nan_index = 3 * timeperiod - 3

        self.date = date[first_not_nan_index+1:]
        self.openp = openp[first_not_nan_index+1:]
        self.closep = closep[first_not_nan_index+1:]
        self.highp = highp[first_not_nan_index+1:]
        self.lowp = lowp[first_not_nan_index+1:]
        self.volumep = volumep[first_not_nan_index+1:]

        self.candle_price = highp - (highp - lowp)/2 #openp - np.fabs(openp - closep)/2

        self.candle_price_for_draw = self.candle_price[first_not_nan_index+1:]

        self.candle_price_TEMA = talib.TEMA(self.candle_price, timeperiod=timeperiod)[first_not_nan_index+1:]


        if verbose:
            # A bit hardcode
            increment_min = int(timeframe[:-1]) if timeframe[-1] == "m" else int(timeframe[:-1])*60

            # Set min max
            self.ui.set_values(
                [
                    self.date[self.window_fetch].replace(tzinfo=datetime.timezone.utc).timestamp(),
                    self.date[-1].replace(tzinfo=datetime.timezone.utc).timestamp(),
                    increment_min
                ], 
                self.date, 
                self.candle_price_TEMA
            )

            date_utc = np.array([ d.replace(tzinfo=datetime.timezone.utc).timestamp()  for d in date ])
            dt_ts = date_utc[first_not_nan_index+1:]
        
            c = 'g'
            br = pg.mkBrush(c)
            pn = pg.mkPen(c, width=1, style=QtCore.Qt.SolidLine)
            plt_top = self.ui.plot1.plot(symbol='o', symbolSize=2, symbolPen=pn, symbolBrush=br)
            plt_top.setPen(c)
            plt_top.setData(dt_ts, self.candle_price_TEMA)

            if self.ui.draw_candles.checkState() == QtCore.Qt.Checked:
                item = monitor_test_misc.CandlestickItem(mts=date_utc, openp=openp, closep=closep, lowp=lowp, highp=highp)
                self.ui.plot1.addItem(item)

            self.ui.plot1.vb.setRange(yRange=(min(lowp), max(highp)) )  # xRange=(min,max), 

        monitor_test_misc.log('Init data fetched. Timeframe: %s, Timeperiod: %s, Data count: %s' % (timeframe, str(timeperiod), str(len(self.candle_price_TEMA)) ))

    def ts_analysis(self, event=None):

        print("Time series analysis for CLOSE position")

        timeperiod = int(self.ui.timeperiod_test.value())

        # Integration
        n = 1
        integr = np.diff(self.closep, n=n)
        date1 = self.date[n:]

        first_not_nan_index = 3 * timeperiod - 3
        date2 = date1[first_not_nan_index+1:]
        _TEMA = talib.TEMA(integr, timeperiod=timeperiod)[first_not_nan_index+1:]

        # Autocorrelation

        fig = plt.figure("Time series analysis for CLOSE position", figsize=(12,8))
        ax0 = fig.add_subplot(411)
        ax0.set_title("Original timeseries (TEMA)")
        ax0.grid()

        ax0.plot(self.date, self.candle_price_TEMA, '-bo')

        ax1 = fig.add_subplot(412, sharex=ax0)
        ax1.set_title("Integrated original timeseries. diff=1 (TEMA)")
        ax1.grid()
        ax1.axis('on')
        # ax1.axhline(0, color='k')
        # ax0.plot(date1, integr, 'b')
        ax1.plot(date2, _TEMA, 'r')

        lags = int(100)
        ax2 = fig.add_subplot(413)
        fig = sm.graphics.tsa.plot_acf(_TEMA, lags=lags, ax=ax2)
        ax3 = fig.add_subplot(414)
        fig = sm.graphics.tsa.plot_pacf(_TEMA, lags=lags, ax=ax3)

        fig.set_tight_layout(True)

        # plt.tight_layout()

        plt.show()

    def draw(self, date, candle_price_for_draw, candle_price_TEMA, orders_history, DIV_PARTS, initial_BTC_wallet, initial_USD_wallet):
        """
            Just draw lines. It does not clean plots before
        """

        def draw_sell_buy():
            for order in orders_history:

                if order["type"] == "sell":
                    angle = -90
                elif order["type"] == "buy":
                    angle = 90

                br = pg.mkBrush(color=pg.intColor(order['index']))
                pn = pg.mkPen(color=pg.intColor(order['index']), width=1, style=QtCore.Qt.SolidLine)
                a = pg.ArrowItem(pos=( order['mts'].replace(tzinfo=datetime.timezone.utc).timestamp(), order['price']), 
                            angle=angle, tipAngle=60, baseAngle=0, headLen=10, tailLen=None, brush=br, pen=pn)
                self.ui.plot1.addItem(a)
                self.ui.plot1_sell_buy.append(a)

                if order['loss'] != 0.0:
                    t = pg.TextItem(text="%.2f" % order['loss'], color=pg.intColor(order['index']), anchor=(0,0))
                    self.ui.plot1.addItem(t)
                    t.setPos( order['mts'].replace(tzinfo=datetime.timezone.utc).timestamp(), order['price'])
                    self.ui.plot1_sell_buy.append(t)

        def get_history_for_one_wallet(index):

            # Get history for wallet
            h = []
            for obj in orders_history:
                try:
                    if obj["index"] == index:
                        h.append(obj)
                except TypeError:
                    pass

            BTC = []
            USD = []

            x = self.date[self.window_fetch].replace(tzinfo=datetime.timezone.utc).timestamp()
            y = initial_BTC_wallet / DIV_PARTS
            x1 = h[0]["mts"].replace(tzinfo=datetime.timezone.utc).timestamp()
            y1 = h[0]["btc_end_in_wallet"]
            is_sold = True if h[0]["btc_init_in_wallet"] == 0 else False
            BTC.append( (x,y,x1,y1,is_sold) )


            x = self.date[self.window_fetch].replace(tzinfo=datetime.timezone.utc).timestamp()
            y = initial_USD_wallet / DIV_PARTS
            x1 = h[0]["mts"].replace(tzinfo=datetime.timezone.utc).timestamp()
            y1 = h[0]["usd_end_in_wallet"]
            is_sold = True if h[0]["usd_init_in_wallet"] == 0 else False
            USD.append( (x,y,x1,y1,is_sold) )


            for i in range(0, len(h) - 1 , 1):

                x = h[i]["mts"].replace(tzinfo=datetime.timezone.utc).timestamp()
                y = h[i]["btc_end_in_wallet"]
                x1 = h[i+1]["mts"].replace(tzinfo=datetime.timezone.utc).timestamp()
                if h[i+1]["btc_end_in_wallet"] == 0:
                    y = h[i]["btc_end_in_wallet"]
                    y1 = y
                else:
                    y = h[i]["btc_init_in_wallet"]
                    y1 = h[i+1]["btc_end_in_wallet"]
                is_sold = True if h[i]["btc_end_in_wallet"] == 0 else False
                BTC.append( (x,y,x1,y1,is_sold) )


                x = h[i]["mts"].replace(tzinfo=datetime.timezone.utc).timestamp()
                y = h[i]["usd_end_in_wallet"]
                x1 = h[i+1]["mts"].replace(tzinfo=datetime.timezone.utc).timestamp()
                if h[i+1]["usd_end_in_wallet"] == 0:
                    y = h[i]["usd_end_in_wallet"]
                    y1 = y
                else:
                    y = h[i]["usd_init_in_wallet"]
                    y1 = h[i+1]["usd_end_in_wallet"]
                is_sold = True if h[i]["usd_end_in_wallet"] == 0 else False
                USD.append( (x,y,x1,y1,is_sold) )

            return BTC, USD

        def zoom(currency):

            if len(orders_history) > 0:
                x_min = min(orders_history, key=lambda x:x['mts'])['mts'].replace(tzinfo=datetime.timezone.utc).timestamp()
                x_max = max(orders_history, key=lambda x:x['mts'])['mts'].replace(tzinfo=datetime.timezone.utc).timestamp()

                y_min = 0.0
                _y_min = []
                _y_max = []
                for order in orders_history:
                    if order[currency + "_init_in_wallet"] > 0.0:
                        _y_min.append(order[currency + "_init_in_wallet"])
                    _y_max.append(order[currency + "_end_in_wallet"])

                if len(_y_min) > 0:
                    y_min = min(_y_min)

                if len(_y_max) > 0:
                    y_max = max(_y_max)

                if currency == "btc":
                    self.ui.plot2.vb.setRange(xRange=(x_min, x_max), yRange=(y_min, y_max), update=True, disableAutoRange=True)
                else:
                    self.ui.plot3.vb.setRange(xRange=(x_min, x_max), yRange=(y_min, y_max), update=True, disableAutoRange=True)

        if self.ui.draw_candles.checkState() == QtCore.Qt.Checked:
            cpd = self.ui.plot1.plot()
            pn = pg.mkPen(color='b', width=2, style=QtCore.Qt.SolidLine)
            cpd.setPen(pn)
            dt_ts = np.array([ d.replace(tzinfo=datetime.timezone.utc).timestamp()  for d in date ])
            cpd.setData(dt_ts, candle_price_for_draw)
            self.ui.plot1_sell_buy.append(cpd)

        draw_sell_buy()

        # Get existing indexes
        existing_indexes = set()
        for order in orders_history:
            existing_indexes.add(order["index"])
        existing_indexes = sorted(list(existing_indexes))

        x_for_range = []
        y_for_range = []
        for index in existing_indexes:
            BTC, USD = get_history_for_one_wallet(index)

            chart = monitor_test_misc.ChartItem(lines=BTC, index=index, plot=self.ui.plot2)
            self.ui.plot2.addItem(chart)

            chart = monitor_test_misc.ChartItem(lines=USD, index=index, plot=self.ui.plot3)
            self.ui.plot3.addItem(chart)

        zoom(currency="usd")
        zoom(currency="btc")

    def calculate_percentage(self, verbose, divided_USD_wallet_last, divided_BTC_wallet_last, orders_history, DIV_PARTS, initial_BTC_wallet, initial_USD_wallet):

        # TODO: Recognize not finished position (except initial). For example started a short but didnt exit.
        def calc_profit_percentage(index):

            # Get history for wallet
            h = []
            for obj in orders_history:
                try:
                    if obj["index"] == index:
                        h.append(obj)
                except TypeError:
                    pass

            if len(h) == 0:
                profit_BTC = "NU"
                profit_USD = "NU"
                return profit_BTC, profit_USD  

            BTC = [  h[0]["btc_init_in_wallet"],  ]
            USD = [  h[0]["usd_init_in_wallet"],  ]
            for obj in h:
                BTC.append( obj["btc_end_in_wallet"] )
                USD.append( obj["usd_end_in_wallet"] )

            # profit for BTC
            if len(BTC) == 1:
                profit_BTC = 0.0
            elif len(BTC) == 2:
                profit_BTC = "TWO"
            elif len(BTC) > 2:
                init = BTC[1] if BTC[0] == 0 else BTC[0]
                if BTC[-1] == 0:
                    profit_BTC = 0.0
                else:
                    profit_BTC = ((BTC[-1] - init) / init ) * 100

            # profit for BTC
            if len(USD) == 1:
                profit_USD = 0.0
            elif len(USD) == 2:
                profit_USD = "TWO"
            elif len(USD) > 2:
                init = USD[1] if USD[0] == 0 else USD[0]
                if USD[-1] == 0:
                    profit_USD = 0.0
                else:
                    profit_USD = ((USD[-1] - init) / init ) * 100

            return profit_BTC, profit_USD

        def calc_profit_percentage_for_all():
            wallet_parts_profit_BTC = []
            wallet_parts_profit_USD = []
            for i in range(DIV_PARTS):
                profit_BTC, profit_USD = calc_profit_percentage(i)
                wallet_parts_profit_BTC.append(profit_BTC)
                wallet_parts_profit_USD.append(profit_USD)

            common_BTC = 0.0
            for i in wallet_parts_profit_BTC:
                if monitor_test_misc.is_digit(i):
                    common_BTC += i

            common_USD = 0.0
            for i in wallet_parts_profit_USD:
                if monitor_test_misc.is_digit(i):
                    common_USD += i

            return wallet_parts_profit_BTC, wallet_parts_profit_USD, common_BTC, common_USD

        if len(orders_history) == 0:
            wallet_parts_profit_BTC = []
            wallet_parts_profit_USD = []
            common_BTC = 0.0
            common_USD = 0.0
        else:
            wallet_parts_profit_BTC, wallet_parts_profit_USD, common_BTC, common_USD = calc_profit_percentage_for_all()

        if verbose:
            print(" ╔═════════════════════════════════════════════════  === Results ===")
            print(" ║ initial USD: " + str(initial_USD_wallet))
            print(" ║ initial BTC: " + str(initial_BTC_wallet))
            print(" ║ ")
            print(" ║ current USD: ")
            print(" ║ " + str(divided_USD_wallet_last))
            print(" ║ current BTC: ")
            print(" ║ " + str(divided_BTC_wallet_last))
            print(" ║ ")
            print(" ║ Take into account only valueable parts:")
            print(" ║ For example for part price changing [0.0, 45.6, 34.6, 65.5, 76.5] - initial=45.6, end=76.5")
            print(" ║ For sequence [45.6, 34.6, 65.5, 76.5] - initial=45.6, end=76.5")
            print(" ║ ")
            print(" ║ None - less than 2 actions for a current wallet")
            print(" ║ NEI - not exited from initial long/short position")
            print(" ║ NU - not used wallet part")
            print(" ║ TWO - was only one order")
            print(" ║ wise USD (percentage per wallet parts): ")
            print(" ║ " + str(wallet_parts_profit_USD))
            print(" ║ wise BTC (percentage per wallet parts): ")
            print(" ║ " + str(wallet_parts_profit_BTC))
            print(" ║ ")
            print(" ║ wise USD (percentage common for wallet): %s%%" % str(common_USD))
            print(" ║ wise BTC (percentage common for wallet): %s%%" % str(common_BTC))
            print(" ║ ")
            print(" ╚══════════════════════════════════════════════════════════════════")

        return wallet_parts_profit_BTC, wallet_parts_profit_USD, common_BTC, common_USD

    def test_strategy(self, event=None, verbose=True, 
        timeframe=None,
        timeperiod=None,
        LPP_count=None,
        EP_gradient_threshold=None,
        LPP_gradients_threshold=None,
        sell_threshold=None,
        buy_threshold=None,
        begin_time=None,
        end_time=None,
        init_last_sell_price=None,
        init_last_buy_price=None,
        initial_BTC_wallet=None,
        initial_USD_wallet=None,
        DIV_PARTS=None,
        independent_last_sell_buy_price_checking=None,
        forse_commit_sell_buy_status_distace=None,
        pair=None):


        self.ui.clear(parts=["strategy"])

        if verbose:
            print("-------------------------------")
            monitor_test_misc.log(" === STRATEGY TEST MODE === ")

        if independent_last_sell_buy_price_checking is None:
            independent_last_sell_buy_price_checking = True if self.ui.independent_last_sell_buy_price_checking_test.checkState() == QtCore.Qt.Checked else False 

        pair = self.ui.pair_test.currentText() if pair is None else pair
        timeframe = self.ui.timeframe_test.currentText() if timeframe is None else timeframe
        timeperiod = int(self.ui.timeperiod_test.value()) if timeperiod is None else timeperiod

        LPP_count = int(self.ui.LPP_count_test.text()) if LPP_count is None else LPP_count
        EP_gradient_threshold = float(self.ui.EP_gradient_threshold_test.text()) if EP_gradient_threshold is None else EP_gradient_threshold
        LPP_gradients_threshold = float(self.ui.LPP_gradients_threshold_test.text()) if LPP_gradients_threshold is None else LPP_gradients_threshold
        sell_threshold = float(self.ui.sell_threshold_test.text()) if sell_threshold is None else sell_threshold
        buy_threshold = float(self.ui.buy_threshold_test.text()) if buy_threshold is None else buy_threshold

        begin_time = self.ui.range_begin_dt.dateTime().toPyDateTime() if begin_time is None else begin_time
        end_time = self.ui.range_end_dt.dateTime().toPyDateTime() if end_time is None else end_time

        forse_commit_sell_buy_status_distace = float(eval(self.ui.forse_commit_sell_buy_status_distace_test.text())) if (forse_commit_sell_buy_status_distace is None) \
                                                    and (self.ui.forse_commit_sell_buy_status_distace_test.text().startswith("#") is False) else forse_commit_sell_buy_status_distace

        init_last_sell_price = float(self.ui.last_sell_price_test.text()) if init_last_sell_price is None else init_last_sell_price
        init_last_buy_price = float(self.ui.last_buy_price_test.text()) if init_last_buy_price is None else init_last_buy_price
        initial_BTC_wallet = float(self.ui.wallet_BTC_init_test.text()) if initial_BTC_wallet is None else initial_BTC_wallet
        initial_USD_wallet = float(self.ui.wallet_USD_init_test.text()) if initial_USD_wallet is None else initial_USD_wallet
        DIV_PARTS = int(self.ui.wallet_parts_test.value()) if DIV_PARTS is None else DIV_PARTS

        # TODO: should check right index <= or <
        begin_datetime_index = np.where(self.date <= begin_time)[0][-1] 
        end_datetime_index = np.where(self.date >= end_time)[0][0] 

        date_init = self.date[      :   begin_datetime_index + 1 ]
        candle_price_init = self.candle_price_for_draw[      :   begin_datetime_index + 1 ]

        # For good work window_fetch has to be enough for calculating TEMA without 'end effects'
        # window_fetch > 100 should be enough
        # window_fetch = 100

        if verbose:
            monitor_test_misc.log("Begin time of test data: " + self.date[begin_datetime_index + 1].strftime("%Y-%m-%d %H:%M:%S:%f") )
            monitor_test_misc.log("End time of test data: " + self.date[end_datetime_index].strftime("%Y-%m-%d %H:%M:%S:%f") )

        strategy = st.Strategy(date=date_init,
                        init_last_sell_price= init_last_sell_price, 
                        init_last_buy_price= init_last_buy_price,
                        initial_BTC_wallet= initial_BTC_wallet, 
                        initial_USD_wallet= initial_USD_wallet, 
                        DIV_PARTS= DIV_PARTS, 
                        timeperiod_TEMA=timeperiod,
                        verbose=verbose,
                        production=False,
                        LPP_count=LPP_count, 
                        EP_gradient_threshold=EP_gradient_threshold, 
                        LPP_gradients_threshold=LPP_gradients_threshold, 
                        sell_threshold=sell_threshold,
                        buy_threshold=buy_threshold,
                        independent_last_sell_buy=independent_last_sell_buy_price_checking,
                        forse_commit_sell_buy_status_distace=forse_commit_sell_buy_status_distace,
                        pair=pair)

        if verbose:
            monitor_test_misc.log("Start testing strategy...")
            print("")
            print(" maker_fee = taker_fee = 0.25")
            print("")
            print("")

        for i in range(begin_datetime_index + 1, end_datetime_index+1):

            date = self.date[ (i + 1) - self.window_fetch : i + 1 ]
            candle_price = self.candle_price_for_draw[ (i + 1) - self.window_fetch : i + 1 ]

            tickers_ask = candle_price[-1]
            tickers_bid = candle_price[-1]

            strategy.calculate(last_N_candle_prices=candle_price, 
                las_N_current_date=date, 
                current_best_ask=tickers_ask, 
                current_best_bid=tickers_bid,
                maker_fee = 0.25,
                taker_fee = 0.25)

        if verbose:
            monitor_test_misc.log("Testing strategy: successfully completed")
            print("")

        wallet_parts_profit_BTC, wallet_parts_profit_USD, common_BTC, common_USD = self.calculate_percentage(
            verbose=verbose,
            divided_USD_wallet_last = strategy.divided_USD_wallet_current, 
            divided_BTC_wallet_last = strategy.divided_BTC_wallet_current, 
            orders_history = strategy.orders_history,
            DIV_PARTS=DIV_PARTS,
            initial_BTC_wallet=initial_BTC_wallet,
            initial_USD_wallet=initial_USD_wallet
        )

        # DRAW
        if verbose:
            self.draw(date = self.date,
                        candle_price_for_draw = self.candle_price_for_draw,
                        candle_price_TEMA = self.candle_price_TEMA,
                        orders_history = strategy.orders_history,
                        DIV_PARTS=DIV_PARTS,
                        initial_BTC_wallet=initial_BTC_wallet,
                        initial_USD_wallet=initial_USD_wallet
            )

        return wallet_parts_profit_BTC, wallet_parts_profit_USD, common_BTC, common_USD

    def get_trades(self, event=None,
        timeframe=None,
        timeperiod=None,
        pair=None):

        pair = self.ui.pair_test.currentText() if pair is None else pair
        timeframe = self.ui.timeframe_test.currentText() if timeframe is None else timeframe
        timeperiod = int(self.ui.timeperiod_test.value()) if timeperiod is None else timeperiod


        trades = monitor_test_misc.trades_manage(action="get_all")

        self.real_trades = trades

        # ﻿[{'init_last_sell_price': '225.5600000000000000000000000000000000000000',
        #    'buy_threshold': '0.8000000000000000000000000000000000000000',
        #    'LPP_gradients_threshold': 0,
        #    'init_last_buy_price': '225.5600000000000000000000000000000000000000',
        #    'profit_BTC': '0.26890002 --> N/A',
        #    'EP_gradient_threshold': 0,
        #    'initial_USD_wallet': '0E-40',
        #    'div_parts': 2,
        #    'timeperiod': 9,
        #    'forse_commit_sell_buy_status_distace': None,
        #    'trading_end_time': '2018-03-20T21:51:30.065',
        #    'statistic_begin_time': '2018-03-19T12:18:00',
        #    'trading_begin_time': '2018-03-20T21:50:37.506',
        #    'orders_history_count': 0,
        #    'LPP_count': 1,
        #    'id': 2,
        #    'independent_last_sell_buy_price_checking': False,
        #    'initial_BTC_wallet': '0.2689000200000000173616854226565919816494',
        #    'profit_USD': '0.0 --> N/A',
        #    'pair_timeframe': 1,
        #    'sell_threshold': '0.8000000000000000000000000000000000000000',
        #    'is_active': False
        #    "pair": pair,
        #    "timeframe": timeframe},
        # ]

        ids = []
        for tr in trades:
            if tr["pair"] == pair:
                if (tr["timeframe"] == timeframe) and (tr["timeperiod"] == timeperiod):
                    trading_begin_time = datetime.datetime.strptime(tr["trading_begin_time"], '%Y-%m-%dT%H:%M:%S.%f')
                    t = str(tr["id"]) + ":" + trading_begin_time.strftime('%Y-%m-%d %H:%M')
                    ids.append(t)

        if len(ids) > 0:
            self.ui.existing_real_trades.setEnabled(True)
            self.ui.show_real_button.setEnabled(True)

        self.ui.existing_real_trades.clear()
        self.ui.existing_real_trades.addItems(reversed(ids))

    def show_real(self, event=None):
        # def to_date(string_date):
        #     # '2018-03-20T21:50:37.506'
        #     return datetime.datetime.strptime(string_date, '%Y-%m-%dT%H:%M:%S.%f')

        self.ui.clear(parts=["strategy"])

        trade_id = int(self.ui.existing_real_trades.currentText().split(":")[0])
        pair = self.ui.pair_test.currentText()

        orders_history = monitor_test_misc.get_orders_history(trade_id=trade_id)

        # [{'usd_end_in_wallet': '27.2244419999999998083239916013553738594055',
        #  'id': 5,
        #  'mts': '2018-03-28T11:26:00',
        #  'btc_end_in_wallet': '0E-40',
        #  'price': '200.0000000000000000000000000000000000000000',
        #  'loss': '0E-40',
        #  'wallet_index': 0,
        #  'amount': '0.1366686400000000078946982284833211451769',
        #  'trade_id': 22,
        #  'usd_init_in_wallet': '0E-40',
        #  'fee_amount': '-0.0545580000000000023274715488241781713441',
        #  'misc': {'USD': [27.224442, 0.0], 'BTC': [0.0, 0.13694228]},
        #  'btc_init_in_wallet': '0.1366686400000000078946982284833211451769',
        #  'fee_currency': 'USD  ',
        #  'kind': 'sell'}, ...]


        if len(orders_history) == 0:
            print("Still no trades... Or negligeable")
            print("Might be first sell or buy!!!")
            return None

        # TODO: Fix this fucking shit!
        for o in range(len(orders_history)):
            orders_history[o].update({"index": orders_history[o]["wallet_index"]})
            orders_history[o].update({"type": orders_history[o]["kind"]})
            orders_history[o]["mts"] = datetime.datetime.strptime(orders_history[o]["mts"], '%Y-%m-%dT%H:%M:%S')
            orders_history[o]["usd_end_in_wallet"] = float(orders_history[o]["usd_end_in_wallet"])
            orders_history[o]["btc_end_in_wallet"] = float(orders_history[o]["btc_end_in_wallet"])
            orders_history[o]["price"] = float(orders_history[o]["price"])
            orders_history[o]["loss"] = float(orders_history[o]["loss"])
            orders_history[o]["amount"] = float(orders_history[o]["amount"])
            orders_history[o]["usd_init_in_wallet"] = float(orders_history[o]["usd_init_in_wallet"])
            orders_history[o]["btc_init_in_wallet"] = float(orders_history[o]["btc_init_in_wallet"])
            orders_history[o]["fee_amount"] = float(orders_history[o]["fee_amount"])

        trade = None
        for tr in self.real_trades:
            if tr["id"] == trade_id:
                trade = tr
                break

        print("")
        print("")
        print("                                ---------------------------------")
        print("                                      === TRADE RESULTS === ")
        print("                                ---------------------------------")
        print("")
        print("")



        st.show_settings(
            pair=pair,
            independent_last_sell_buy=trade["independent_last_sell_buy_price_checking"],
            forse_commit_sell_buy_status_distace=trade["forse_commit_sell_buy_status_distace"],
            timeframe=trade["timeframe"],
            timeperiod_TEMA=trade["timeperiod"],
            LPP_count=trade["LPP_count"],
            EP_gradient_threshold=trade["EP_gradient_threshold"],
            LPP_gradients_threshold=trade["LPP_gradients_threshold"],
            sell_threshold=trade["sell_threshold"],
            buy_threshold=trade["buy_threshold"],
            init_last_sell_price=trade["init_last_sell_price"],
            init_last_buy_price=trade["init_last_buy_price"],
            initial_BTC_wallet=trade["initial_BTC_wallet"],
            initial_USD_wallet=trade["initial_USD_wallet"],
            DIV_PARTS=trade["div_parts"],
            start_trading= datetime.datetime.strptime(trade["trading_begin_time"], '%Y-%m-%dT%H:%M:%S.%f'))


        wallet_parts_profit_BTC, wallet_parts_profit_USD, common_BTC, common_USD = self.calculate_percentage(
            verbose=True,
            divided_USD_wallet_last = orders_history[-1]['misc']['USD'], 
            divided_BTC_wallet_last = orders_history[-1]['misc']['BTC'], 
            orders_history = orders_history,
            DIV_PARTS=trade["div_parts"],
            initial_BTC_wallet=float(trade["initial_BTC_wallet"]),
            initial_USD_wallet=float(trade["initial_USD_wallet"])
        )

        self.draw(date = self.date,
                    candle_price_for_draw = self.candle_price_for_draw,
                    candle_price_TEMA = self.candle_price_TEMA,
                    orders_history = orders_history,
                    DIV_PARTS=trade["div_parts"],
                    initial_BTC_wallet=float(trade["initial_BTC_wallet"]),
                    initial_USD_wallet=float(trade["initial_USD_wallet"])
        )

        return None

    def investigate_strategy(self, event=None):

        parameters = {
            "timeframe":                                    ['5m'],
            "timeperiod":                                   [3, 9, 15, 30],
            "LPP_count":                                    [1], # >= 1
            "EP_gradient_threshold":                        [0.0],
            "LPP_gradients_threshold":                      [0.0],
            "sell_threshold":                               [0.8],
            "buy_threshold":                                [0.8],
            "DIV_PARTS":                                    [1, 3, 5],
            "initial_BTC_wallet":                           [0.0],
            "initial_USD_wallet":                           [1.0],
            "independent_last_sell_buy_price_checking":     [None],  # if None, a value is taken from UI
            "forse_commit_sell_buy_status_distace":         [None],  # if None, a value is taken from UI
            "pair":                                         [None],  # if None, a value is taken from UI
            "step":                                         [2, 5]   # Testing step. 
                                                                     # 50*timeframe = step in minutes or hours depends on timeframe unit
        }

        # A window for calculation TEMA
        window_TEMA = 100 

        print("                 ╔════════════════════════════════════════════════╗")
        print("                 ║           ++++ Testing strategy ++++           ║")
        print("                 ╚════════════════════════════════════════════════╝")
        print("")
        print("Parameters:")
        # print("Testing step: " + str(step))
        print(json.dumps(parameters, indent=4))
        print("")
        monitor_test_misc.log(" Strat...")
        print("")

        
        parameters_names = sorted(parameters)
        combinations = itertools.product(*(parameters[name] for name in parameters_names))
        parameters_combinations = []
        for values in combinations:
            d = dict(zip(parameters_names, values))
            parameters_combinations.append(d)

        # parameters_combinations:
        # {'EP_gradient_thresholds': 0.0, 'DIV_PARTS': 1, 'LPP_gradients_thresholds': 0.0, 'timeperiods': 9, 'timeframes': '30m', 'sell_thresholds': 0.8, 'buy_threshold': 0.8, 'LPP_counts': 2}
        # {'EP_gradient_thresholds': 0.0, 'DIV_PARTS': 1, 'LPP_gradients_thresholds': 0.0, 'timeperiods': 9, 'timeframes': '1m', 'sell_thresholds': 0.8, 'buy_threshold': 0.8, 'LPP_counts': 2}
        # {'EP_gradient_thresholds': 0.0, 'DIV_PARTS': 3, 'LPP_gradients_thresholds': 0.0, 'timeperiods': 9, 'timeframes': '30m', 'sell_thresholds': 0.8, 'buy_threshold': 0.8, 'LPP_counts': 2}
        # ...

        good_parameters = []
        current_timeframe = parameters_combinations[0]["timeframe"]
        current_timeperiod = parameters_combinations[0]["timeperiod"]
        i = 0
        for current_parameters in parameters_combinations:
            i += 1
            monitor_test_misc.log("Testing combination %s of %s:" % (str(i), str(len(parameters_combinations))))
            print("Parameters: " + str(current_parameters))
            print("")

            # Fetch data if needed
            if (current_parameters["timeframe"] != current_timeframe) or (current_parameters["timeperiod"] != current_timeperiod):
                self.fetch_data(
                    verbose=True, 
                    timeframe=current_parameters["timeframe"],
                    timeperiod=current_parameters["timeperiod"],
                    window_fetch=window_TEMA,
                    pair=None # Get from UI
                )
                current_timeframe = current_parameters["timeframe"]
                current_timeperiod = current_parameters["timeperiod"]

            # begin_datetime_index = np.where(self.date <= self.ui.range_begin_dt.dateTime().toPyDateTime())[0][-1] 

            current_step = current_parameters["step"]

            print("MIN date: " + self.date[current_step].strftime("%Y-%m-%d %H:%M:%S:%f") )
            print("MAX date: " + self.date[-1].strftime("%Y-%m-%d %H:%M:%S:%f") )
            print("++++++++ intermediate results: ")
            print("")

            

            current_begin_index = window_TEMA - current_step
            timeseties_length = len(self.date)
            is_profitable_parameters = True
            current_profit = []

            while (timeseties_length - current_begin_index) >= 2*current_step:
                current_begin_index += current_step

                # Current last buy and sell prices. Just current TEMA price
                cerrent_last_buy_price = self.candle_price_for_draw[current_begin_index]
                current_last_sell_price = self.candle_price_for_draw[current_begin_index]

                wallet_parts_profit_BTC, wallet_parts_profit_USD, common_BTC, common_USD = self.test_strategy(
                    verbose=False, 
                    timeframe=current_parameters["timeframe"],
                    timeperiod=current_parameters["timeperiod"],
                    LPP_count=current_parameters["LPP_count"],
                    EP_gradient_threshold=current_parameters["EP_gradient_threshold"],
                    LPP_gradients_threshold=current_parameters["LPP_gradients_threshold"],
                    sell_threshold=current_parameters["sell_threshold"],
                    buy_threshold=current_parameters["buy_threshold"],
                    begin_time=             self.date[current_begin_index],
                    end_time=               self.date[-1],
                    init_last_sell_price=   current_last_sell_price,
                    init_last_buy_price=    cerrent_last_buy_price,
                    initial_BTC_wallet=current_parameters["initial_BTC_wallet"],
                    initial_USD_wallet=current_parameters["initial_USD_wallet"],
                    DIV_PARTS=current_parameters["DIV_PARTS"],
                    independent_last_sell_buy_price_checking=current_parameters["independent_last_sell_buy_price_checking"],
                    forse_commit_sell_buy_status_distace=current_parameters["forse_commit_sell_buy_status_distace"],
                    pair=current_parameters["pair"]
                )
                print(str(wallet_parts_profit_USD))

                if all(monitor_test_misc.is_digit(v) for v in wallet_parts_profit_USD):
                    if all( v >= 0 for v in wallet_parts_profit_USD):
                        current_profit.append( (common_USD, common_BTC) )
                        continue
                    else:
                        is_profitable_parameters = False
                        break
                else:
                    is_profitable_parameters = False
                    break

            if is_profitable_parameters:
                monitor_test_misc.log("Testing combination %s of %s : %s" % (str(i), str(len(parameters_combinations)), str(True)))
                # print(current_parameters)
                good_parameters.append((current_parameters, current_profit))
            else:
                monitor_test_misc.log("Testing combination %s of %s : %s" % (str(i), str(len(parameters_combinations)), str(False)))
                # print(current_parameters)

            print("--------------------------------------------------------------------------------------------------")

        print("")
        print("")
        monitor_test_misc.log("Finish")
        print("                 ╔═══════════════════════════════════════╗")
        print("                 ║           ++++ RESULTS ++++           ║")
        print("                 ╚═══════════════════════════════════════╝")
        print("")
        for i in good_parameters:
            print("▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀")
            print("Parameters: " + str(i[0]))
            print("")
            print("USD_wallet_profit: " + str(i[1][0]))
            print("BTC_wallet_profit: " + str(i[1][1]))
            print("▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄")

        print("                 ╔═════════════════════════════════════════════════════════╗")
        print("                 ║           ++++ Testing has beed FINISHED ++++           ║")
        print("                 ╚═════════════════════════════════════════════════════════╝")

        return None


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    app.exec_()
