import sys
import os
application_dir = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(application_dir, "misc", "img")
sys.path.append(application_dir)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import datetime

import requests
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np

# If you recreated a new gui.py: GraphicsWindow()#self.tab)
from gui.gui import *
from server.settings import SERVER_ENDPOINT as ENDPOINT



def log(line):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f") + ": " + line)

def is_digit(g):
    try:
        g = float(g)
    except Exception:
        return False
    return True

def dict_json_str(d):
    return json.dumps(d, sort_keys=True, indent=5, separators=(',', ': '))

# ==========================================================
#           Backend interaction
# ==========================================================

def balance():
    r = requests.get(ENDPOINT + "balance/")
    try:
        r_json = r.json()
    except json.decoder.JSONDecodeError:
        return r.text
    return r_json

def pair(action, pair="", timeframe=""):
    """

    Args:
        action: "delete", "get", "put", "get_all"
        pair:
        timeframe:

    Returns:

    """
    data = {
              "pair": pair,
              "timeframe": timeframe,
              "action": action
    }

    data = json.dumps(data)
    r = requests.post(ENDPOINT + "pairs/", data=data)

    try:
        r_json = r.json()
    except json.decoder.JSONDecodeError:
        return r.text

    if action == "get_all":
        if len(r.json()) == 0:
            return None
        p_t = dict()
        for i in range(len(r_json)):
            try:
                p_t[r_json[i]["pair"]].append(r_json[i]["timeframe"])
            except KeyError:
                p_t[r_json[i]["pair"]] = [r_json[i]["timeframe"],]

        return p_t

    return r_json

def fetch_candles(pair, timeframe):
    """

    Response:
        [{'pair_timeframe_id': 4, 'mts': datetime.datetime(2018, 3, 9, 8, 50), 'close': 253.66, 'open': 255.1, 'volume': 304.23869907, 'high': 255.41, 'low': 253.2, 'id': 300},
        {'pair_timeframe_id': 4, 'mts': datetime.datetime(2018, 3, 9, 8, 55), 'close': 252.88, 'open': 253.14, 'volume': 894.48258349, 'high': 253.15, 'low': 251.19, 'id': 299},
        {'pair_timeframe_id': 4, 'mts': datetime.datetime(2018, 3, 9, 9, 0), 'close': 251.7, 'open': 251.77, 'volume': 97.97269972, 'high': 252.74, 'low': 251.7, 'id': 298},
        {'pair_timeframe_id': 4, 'mts': datetime.datetime(2018, 3, 9, 9, 5), 'close': 250.6, 'open': 252.16, 'volume': 294.86293512, 'high': 253.29, 'low': 250.02, 'id': 297},
        {'pair_timeframe_id': 4, 'mts': datetime.datetime(2018, 3, 9, 9, 10), 'close': 247.3, 'open': 250.01, 'volume': 917.4697301, 'high': 250.01, 'low': 247.3, 'id': 296},
        {'pair_timeframe_id': 4, 'mts': datetime.datetime(2018, 3, 9, 9, 15), 'close': 248.46, 'open': 247.74, 'volume': 199.52402397, 'high': 248.49, 'low': 247.7, 'id': 295},
        {'pair_timeframe_id': 4, 'mts': datetime.datetime(2018, 3, 9, 10, 40), 'close': 252.22, 'open': 255.94, 'volume': 283.23386402, 'high': 255.95, 'low': 252.16, 'id': 181}]

    """

    # TODO: date fetched/deserialized as "2018-03-19T15:18:00". should be returned datetime

    data = {
              "pair": pair,
              "timeframe": timeframe,
              "action": "get"
    }

    data = json.dumps(data)
    r = requests.post(ENDPOINT + "candles/", data=data)
    rrr = r.json()

    for i in range(len(rrr)):
        for k, v in rrr[i].items():

            if not isinstance(v, str):
                continue

            try:
                dt = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
            except Exception:
                dt = None

            try:
                f = float(v)
            except Exception:
                f = None

            if isinstance(dt, datetime.datetime):
                rrr[i][k] = dt
            elif isinstance(f, float):
                rrr[i][k] = f

    date = np.array([])
    openp = np.array([])
    closep = np.array([])
    highp = np.array([])
    lowp = np.array([])
    volumep = np.array([])

    for i in range(len(rrr)):
        for k, v in rrr[i].items():
            if k == "mts":
                date_ = datetime.datetime.strptime(rrr[i][k], '%Y-%m-%dT%H:%M:%S')
                date = np.append(date_, date)
            elif k == "open":
                openp = np.append(rrr[i][k], openp)
            elif k == "close":
                closep = np.append(rrr[i][k], closep)
            elif k == "high":
                highp = np.append(rrr[i][k], highp)
            elif k == "low":
                lowp = np.append(rrr[i][k], lowp)
            elif k == "volume":
                volumep = np.append(rrr[i][k], volumep)

    return date, openp, closep, highp, lowp, volumep

def collector(action):
    data = {
              "action": action # "stop" # "start"  # "stop", "status"
    }
    data = json.dumps(data)
    r = requests.post(ENDPOINT + "collector/", data=data)
    if action == "status":
        return r.json()
    r = dict_json_str(r.json())
    return r

def crypto_trader_bot(action, trader_start_conditions=None):
    data = {
              "action": action # "stop" # "start", "status"
    }
    if trader_start_conditions is not None:
        data.update(trader_start_conditions)
    data = json.dumps(data)
    r = requests.post(ENDPOINT + "crypto_trader_bot/", data=data)
    if (action == "status") or (action == "short_status"):
        return r.json()
    r = dict_json_str(r.json())
    return r

def candle(action, pair="", timeframe=""):
    """

    Args:
        action: "get" #, "delete", "delete_all", "count"
        pair:
        timeframe:

    Returns:

    """
    data = {
              "pair": pair,
              "timeframe": timeframe,
              "action": action
    }

    data = json.dumps(data)
    r = requests.post(ENDPOINT + "candles/", data=data)

    try:
        r_json = r.json()
    except json.decoder.JSONDecodeError:
        return r.text

    return r_json

def trades_manage(action, trade_id=None):
    """

    Args:
        action: "delete", "get", "get_all"
        trade_id:

    Returns:

    """
    data = {
              "id": trade_id,
              "action": action
    }

    data = json.dumps(data)
    r = requests.post(ENDPOINT + "trade/", data=data)

    try:
        r_json = r.json()
    except json.decoder.JSONDecodeError:
        return r.text

    return r_json

def get_orders_history(trade_id):
    """

        Args:
            action: "delete", "get", "get_all"
            pair:
            timeframe:

        Returns:

        """
    data = {
        "trade_id": int(trade_id),
        "action": "get_all"
    }

    data = json.dumps(data)
    r = requests.post(ENDPOINT + "orders_history/", data=data)

    try:
        r_json = r.json()
    except json.decoder.JSONDecodeError:
        return r.text

    return r_json


# ==========================================================
#           Custom items for plot
# ==========================================================

class ChartItem(pg.GraphicsObject):
    def __init__(self, lines, index, plot):
        pg.GraphicsObject.__init__(self)
        self.lines = lines
        self.index = index
        self.plot = plot

        self.generatePicture()
    
    def generatePicture(self):
        ## pre-computing a QPicture object allows paint() to run much more quickly, 
        ## rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setOpacity(1.0)

        for i in range(len(self.lines)):

            line = self.lines[i]

            if line[4]:
                p.setPen(pg.mkPen(color=pg.intColor(self.index), width=2, style=QtCore.Qt.DotLine) ) #DashLine) )
            else:
                p.setPen(pg.mkPen(color=pg.intColor(self.index), width=2, style=QtCore.Qt.SolidLine) )

            p.drawLine(QtCore.QLineF(line[0], line[1], line[2], line[3]))

        if len(self.lines) > 0:

            p_date = []
            p_values = []
            for i in range(len(self.lines)):
                line = self.lines[i]
                p_date.append(line[0])
                p_values.append(line[1])

            p_date.append(self.lines[-1][2])
            p_values.append(self.lines[-1][3])

            color = pg.intColor(self.index)
            br = pg.mkBrush(color=color)
            pn = pg.mkPen(color=color, width=2, style=QtCore.Qt.SolidLine)
            # pn1 = pg.mkPen(color=color, width=0, style=QtCore.Qt.SolidLine)
            cpd = self.plot.plot(symbol='o', symbolSize=3, pen=None, symbolPen=pn, symbolBrush=br)
            # cpd.setPen(pn1)
            cpd.setData(p_date, p_values)
            # self.ui.plot1_sell_buy.append(cpd)

        p.end()
    
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    
    def boundingRect(self):
        ## boundingRect _must_ indicate the entire area that will be drawn on
        ## or else we will get artifacts and possibly crashing.
        ## (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, mts, openp, closep, lowp, highp):
        pg.GraphicsObject.__init__(self)
        # data = [  ## fields are (time, open, close, min, max).
        #     (1., 10, 13, 5, 15),
        #     (2., 13, 17, 9, 20),
        #     (3., 17, 14, 11, 23),
        #     (4., 14, 15, 5, 19),
        #     (5., 15, 9, 8, 22),
        #     (6., 9, 15, 8, 16),
        # ]
        self.data = []
        for i in range(len(mts)):
            self.data.append( (mts[i], openp[i], closep[i], lowp[i], highp[i]) )
        self.generatePicture()
    
    def generatePicture(self):
        ## pre-computing a QPicture object allows paint() to run much more quickly, 
        ## rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setOpacity(0.7)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, openr, closer, lowr, highr) in self.data:
            p.drawLine(QtCore.QPointF(t, lowr), QtCore.QPointF(t, highr))
            if openr > closer:
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setBrush(pg.mkBrush('g'))
            p.drawRect(QtCore.QRectF(t-w, openr, w*2, closer-openr))
        p.end()
    
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    
    def boundingRect(self):
        ## boundingRect _must_ indicate the entire area that will be drawn on
        ## or else we will get artifacts and possibly crashing.
        ## (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label.rotate(45)

        # self.setTickSpacing(5, 1)

    def tickStrings(self, values, scale, spacing):
        return [ datetime.datetime.utcfromtimestamp(value).strftime("%Y-%m-%d\n%H:%M:%S")  for value in values]

# ==========================================================
#           Overrided UI form (gui.py)
# ==========================================================

class Ui_Form(Ui_MainWindow):

    def setupUi_over(self, MainWindow):
        self.setupUi(MainWindow)
        self.center(MainWindow)

        MainWindow.setWindowIcon(QtGui.QIcon( os.path.join(img_dir, 'icon.png')))
        pm = QtGui.QPixmap(os.path.join(img_dir, 'info.png'))
        pm = pm.scaled(pm.width()/2.5, pm.height()/2.5, transformMode=QtCore.Qt.SmoothTransformation)
        self.label_info.setPixmap(pm)

        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(0, 247, 44)
        pal.setColor(QtGui.QPalette.Text, textc)
        font = QtGui.QFont("Courier")
        font.setPointSize(12)
        self.trader_log.setPalette(pal)
        self.collector_log.setPalette(pal)
        self.trader_log.setFont(font)
        self.collector_log.setFont(font)

        font = QtGui.QFont()
        font.setPixelSize(9)

        self.update_pairs_timeframes()

        self.plt_text_label = dict()
        # ===============================================================
        #                      Top plot
        # ===============================================================
        self.candles_graph.scene().sigMouseClicked.connect(self.on_click_plot)        
        self.plot1 = self.candles_graph.addPlot(title='Triple Exponential Moving Average of time series (candles)', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot1.getAxis("bottom").tickFont = font
        self.plot1.getAxis("left").tickFont = font
        self.plot1.showGrid(x = True, y = True, alpha = 0.7)
        self.candles_graph.show()

        self.plot1_sell_buy = []
        

        # ===============================================================
        #                      Left plot
        # ===============================================================
        self.BTC_graph.scene().sigMouseClicked.connect(self.on_click_plot)
        self.plot2 = self.BTC_graph.addPlot(title='Divided BTC wallet', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot2.getAxis("bottom").tickFont = font
        self.plot2.getAxis("left").tickFont = font
        # self.plot2.addLegend()
        self.plot2.showGrid(x = True, y = True, alpha = 0.7)
        self.BTC_graph.show()

        # ===============================================================
        #                      Right plot
        # ===============================================================
        self.USD_graph.scene().sigMouseClicked.connect(self.on_click_plot)
        self.plot3 = self.USD_graph.addPlot(title='Divided USD wallet', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot3.getAxis("bottom").tickFont = font
        self.plot3.getAxis("left").tickFont = font
        # self.plot3.addLegend()
        self.plot3.showGrid(x = True, y = True, alpha = 0.7)
        self.USD_graph.show()


        # ===============================================================
        #                      Scroll range
        # ===============================================================
        self.data = {
            "begin_datetime": None,
            "end_datetime": None
        }

        self.begin_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=4, style=QtCore.Qt.SolidLine))
        self.begin_vLine_USD = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=4, style=QtCore.Qt.SolidLine))
        self.begin_vLine_BTC = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=4, style=QtCore.Qt.SolidLine))

        self.top_midway_hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('y', width=2, style=QtCore.Qt.DotLine))#  DashLine))
        self.bottom_midway_hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('r', width=2, style=QtCore.Qt.DotLine))#  DashLine))


        self.end_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('m', width=4, style=QtCore.Qt.SolidLine))
        self.plot1.addItem(self.begin_vLine, ignoreBounds=True)
        self.plot2.addItem(self.begin_vLine_BTC, ignoreBounds=True)
        self.plot3.addItem(self.begin_vLine_USD, ignoreBounds=True)

        self.plot1.addItem(self.top_midway_hLine, ignoreBounds=True)
        self.plot1.addItem(self.bottom_midway_hLine, ignoreBounds=True)

        self.plot1.addItem(self.end_vLine, ignoreBounds=True)


        # ===============================================================
        #                      Connections
        # ===============================================================
        self.range_begin_dt.dateTimeChanged.connect(self.value_dt_changed_begin)
        self.range_end_dt.dateTimeChanged.connect(self.value_dt_changed_end)

        self.slider_begin.valueChanged.connect(self.value_changed_begin)
        self.slider_end.valueChanged.connect(self.value_changed_end)


        # ===============================================================
        #                      TAB - TEST STRATEGY
        # ===============================================================

        self.pair_test.currentIndexChanged.connect(self.pair_changed)
        self.clear_main_plot_button.clicked.connect(self.clear_main_plot)


        # ===============================================================
        #                      TAB - TEST STRATEGY - SETTINGS
        # ===============================================================



        # ===============================================================
        #                      TAB - BACKEND - TRADER
        # ===============================================================


        self.pair_trader.currentIndexChanged.connect(self.pair_changed)
        self.trader_status_button.clicked.connect(self.trader_status)
        self.trader_status_short_button.clicked.connect(self.trader_status_short)

        self.trader_start_button.clicked.connect(self.trader_start)

        self.trader_stop_button.clicked.connect(self.trader_stop)


        # ===============================================================
        #                      TAB - BACKEND - COLLECTOR
        # ===============================================================

        self.collector_status_button.clicked.connect(self.collector_status)

        self.collector_start_button.clicked.connect(self.collector_start)

        self.collector_stop_button.clicked.connect(self.collector_stop)

        self.fetch_available_balance_button.clicked.connect(self.fetch_available_balance)

        self.pair_add_to_collect_button.clicked.connect(self.pair_add_to_collect)

        self.pair_remove_from_collect_button.clicked.connect(self.pair_remove_from_collect)



        self.candles_clear_all_button.clicked.connect(self.candles_clear_DB_ALL)

        self.candles_info_button.clicked.connect(self.candles_info)

        # -------------------------------------
        # Trades history tree
        # -------------------------------------

        self.trades_history_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.trades_history_tree.customContextMenuRequested.connect(self.trades_history_tree_menu)
        self.trades_history_tree_populate()

    def update_pairs_timeframes(self):
        self.pairs_timeframes = pair(action="get_all")

        self.pair_test.clear()
        self.pair_trader.clear()
        self.timeframe_test.clear()
        self.timeframe_trader.clear()

        if self.pairs_timeframes is None:
            self.pair_test.addItems([])
            self.timeframe_test.addItems([])
            self.pair_trader.addItems([])
            self.timeframe_trader.addItems([])
        else:
            self.pair_test.addItems(list(self.pairs_timeframes.keys()))
            self.timeframe_test.addItems(self.pairs_timeframes[self.pair_test.currentText()])
            self.pair_trader.addItems(list(self.pairs_timeframes.keys()))
            self.timeframe_trader.addItems(self.pairs_timeframes[self.pair_trader.currentText()])

    def trades_history_tree_populate(self):
        self.trades_history_tree.clear()
        trades = trades_manage(action="get_all")

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

        self.trades_history_tree.setColumnCount(5)
        self.trades_history_tree.setHeaderLabels(["pair_tf_tp",
                                                  "trading_begin_time",
                                                  "orders_history_count",
                                                  "profit_BTC",
                                                  "profit_USD",
                                                  "id"])

        for trade in trades:
            trading_begin_time = datetime.datetime.strptime(trade["trading_begin_time"], '%Y-%m-%dT%H:%M:%S.%f')
            t = QtGui.QTreeWidgetItem([
                trade["pair"] + "::" + trade["timeframe"] + "::" + str(trade["timeperiod"]),
                trading_begin_time.strftime('%Y-%m-%d %H:%M'),
                str(trade["orders_history_count"]),
                trade["profit_BTC"],
                trade["profit_USD"],
                str(trade["id"])
            ])
            self.trades_history_tree.addTopLevelItem(t)

        self.trades_history_tree.resizeColumnToContents(0)
        self.trades_history_tree.resizeColumnToContents(1)
        self.trades_history_tree.resizeColumnToContents(2)
        self.trades_history_tree.resizeColumnToContents(3)
        self.trades_history_tree.resizeColumnToContents(4)
        self.trades_history_tree.resizeColumnToContents(5)
        self.trades_history_tree.resizeColumnToContents(6)

    def trades_history_tree_menu(self, position):
        menu = QtWidgets.QMenu()
        delete_trade = QtWidgets.QAction('Delete', menu)
        refresh_all_trades = QtWidgets.QAction('Refresh all', menu)
        delete_trade.triggered.connect(self.trades_history_tree_delete)
        refresh_all_trades.triggered.connect(self.trades_history_tree_populate)
        menu.addAction(delete_trade)
        menu.addAction(refresh_all_trades)
        menu.exec_(self.trades_history_tree.viewport().mapToGlobal(position))

    def trades_history_tree_delete(self):
        selected_items = self.trades_history_tree.selectedItems()
        for item in selected_items:
            trade_id = int(item.text(5))
            trades_manage(action="delete", trade_id=trade_id)
        self.trades_history_tree_populate()


    def collector_status(self, event=None):
        r = collector(action="status")
        kek = "Collector status: \n\n"
        kek += "Status: " + str(r["is_alive"]) + "\n\n"
        kek += "Log: \n" + r["log"]
        self.collector_log.clear()
        self.collector_log.append(kek)

    def collector_start(self, event=None):
        r = collector(action="start")
        r = "Collector start: \n\n" + r
        r += "\n\nWait for a while before starting the collection. (couple of minutes)"
        self.collector_log.clear()
        self.collector_log.append(r)

    def collector_stop(self, event=None):
        r = collector(action="stop")
        r = "Collector stop: \n\n" + r
        self.collector_log.clear()
        self.collector_log.append(r)

    def fetch_available_balance(self):
        r = balance()
        kek = "Available balance on your account:\n\n" + dict_json_str(r)
        self.trader_log.clear()
        self.trader_log.append(kek)

    def pair_add_to_collect(self, event=None):
        p_t = self.collector_pair_timeframe.text().split("::")
        if len(p_t) != 2:
            self.collector_log.setText("Error input data")
            return None
        r1 = collector(action="stop")
        kek = "Collector has been stopped.\n\n"
        pair_ = p_t[0]
        timeframe_ = p_t[1]
        r = pair(action="put", pair=pair_, timeframe=timeframe_)
        r = dict_json_str(r)
        kek += "ADD Pairs into Database: \n\n" + r
        kek += "\n\nNote: Restart collector manually!"
        self.collector_log.clear()
        self.collector_log.append(kek)
        self.update_pairs_timeframes()

    def pair_remove_from_collect(self, event=None):
        p_t = self.collector_pair_timeframe.text().split("::")
        if len(p_t) != 2:
            self.collector_log.setText("Error input data")
            return None
        r1 = collector(action="stop")
        kek = "Collector has been stopped.\n\n"
        pair_ = p_t[0]
        timeframe_ = p_t[1]
        r = pair(action="delete", pair=pair_, timeframe=timeframe_)
        r = dict_json_str(r)
        kek += "DELETE Pairs from Database: \n\n" + r
        kek += "\n\nNote: Restart collector manually!"
        self.collector_log.clear()
        self.collector_log.append(kek)
        self.update_pairs_timeframes()

    def candles_clear_DB_ALL(self):
        r1 = collector(action="stop")
        kek = "Collector has been stopped.\n\n"
        r = candle(action="delete_all")
        r = dict_json_str(r)
        kek += "All candles data have been deleted from Database: \n\n" + r
        self.collector_log.clear()
        self.collector_log.append(kek)

    def candles_info(self):
        p_t = self.collector_pair_timeframe.text().split("::")
        if len(p_t) != 2:
            r = candle(action="count")
        else:
            pair_ = p_t[0]
            timeframe_ = p_t[1]
            r = candle(action="count", pair=pair_, timeframe=timeframe_)
        r = dict_json_str(r)
        kek = "Candles summary from Database: \n\n" + r
        self.collector_log.clear()
        self.collector_log.append(kek)

    def trader_status(self, event=None):
        pair = self.pair_trader.currentText()
        trader_start_conditions = {
            "pair": pair
        }
        r = crypto_trader_bot(action="status", trader_start_conditions=trader_start_conditions)
        kek = "Crypto Trader Bot STATUS: \n\n"
        # kek += "Out file: \n" + r["out_file"]
        kek += "\n\nLog file: \n" + r["log_file"]
        kek += "\n\nStatus: " + str(r["is_alive"])

        self.trader_log.clear()
        self.trader_log.append(kek)

    def trader_status_short(self, event=None):
        pair = self.pair_trader.currentText()
        trader_start_conditions = {
            "pair": pair
        }
        r = crypto_trader_bot(action="short_status", trader_start_conditions=trader_start_conditions)
        kek = "Crypto Trader Bot short STATUS(last 228 lines): \n\n"
        # kek += "Out file: \n" + r["out_file"]
        kek += "\n\nLog file: \n" + r["log_file"]
        kek += "\n\nStatus: " + str(r["is_alive"])

        self.trader_log.clear()
        self.trader_log.append(kek)

    def trader_start(self, event=None):

        if self.independent_last_sell_buy_price_checking_trader.checkState() == QtCore.Qt.Checked:
            independent_last_sell_buy_price_checking = "True"
        else:
            independent_last_sell_buy_price_checking = "False"

        fcsb = self.forse_commit_sell_buy_status_distace_trader.text()
        if fcsb.startswith("#"):
            forse_commit_sell_buy_status_distace = "None"
        else:
            forse_commit_sell_buy_status_distace = str(eval(fcsb))

        trader_start_conditions = {
                    "pair": self.pair_trader.currentText(),
                    "timeframe": self.timeframe_trader.currentText(),
                    "timeperiod": self.timeperiod_trader.text(),
                    "init_last_sell_price": self.last_sell_price_trader.text(),
                    "init_last_buy_price": self.last_buy_price_trader.text(),
                    "DIV_PARTS": self.wallet_parts_trader.text(),
                    "LPP_count": self.LPP_count_trader.text(),
                    "EP_gradient_threshold": self.EP_gradient_threshold_trader.text(),
                    "LPP_gradients_threshold": self.LPP_gradients_threshold_trader.text(),
                    "sell_threshold": self.sell_threshold_trader.text(),
                    "buy_threshold": self.buy_threshold_trader.text(),
                    "independent_last_sell_buy_price_checking": independent_last_sell_buy_price_checking,
                    "forse_commit_sell_buy_status_distace": forse_commit_sell_buy_status_distace
        }

        r = crypto_trader_bot(action="start", trader_start_conditions=trader_start_conditions)
        r = "Crypto Trader Bot has been STARTED: \n\n" + r
        self.trader_log.clear()
        self.trader_log.append(r)

    def trader_stop(self, event=None):
        pair = self.pair_trader.currentText()
        trader_start_conditions = {
            "pair": pair
        }
        r = crypto_trader_bot(action="stop", trader_start_conditions=trader_start_conditions)
        r = "Crypto Trader Bot has been STOPPED: \n\n" + r
        self.trader_log.setText(r)

    def pair_changed(self, i):
        print(self.pairs_timeframes)
        if self.pairs_timeframes is None:
            return None
        self.timeframe_test.clear()
        self.timeframe_test.addItems(self.pairs_timeframes[self.pair_test.currentText()])
        self.timeframe_trader.clear()
        self.timeframe_trader.addItems(self.pairs_timeframes[self.pair_trader.currentText()])







    def clear_main_plot(self):
        self.clear(parts=["top", "strategy"])

    def clear(self, parts):

        if "top" in parts:
            self.plot1.clear()

            self.begin_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=4, style=QtCore.Qt.SolidLine))
            self.end_vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('m', width=4, style=QtCore.Qt.SolidLine))
            self.plot1.addItem(self.begin_vLine, ignoreBounds=True)
            self.plot1.addItem(self.end_vLine, ignoreBounds=True)

            self.top_midway_hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('y', width=2, style=QtCore.Qt.DotLine))#  DashLine))
            self.bottom_midway_hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('r', width=2, style=QtCore.Qt.DotLine))#  DashLine))
            self.plot1.addItem(self.top_midway_hLine, ignoreBounds=True)
            self.plot1.addItem(self.bottom_midway_hLine, ignoreBounds=True)

        if "strategy" in parts:

            self.plot2.clear()
            self.plot3.clear()

            self.begin_vLine_BTC = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=4, style=QtCore.Qt.SolidLine))
            self.begin_vLine_USD = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=4, style=QtCore.Qt.SolidLine))
            self.plot2.addItem(self.begin_vLine_BTC, ignoreBounds=True)
            self.plot3.addItem(self.begin_vLine_USD, ignoreBounds=True)

            # self.win_pg_left.scene().removeItem(self.plot2.legend)
            # self.win_pg_right.scene().removeItem(self.plot3.legend)

            # self.plot2.addLegend()
            # self.plot3.addLegend()

            for item in self.plot1_sell_buy:
                self.plot1.removeItem(item)

            self.plot1_sell_buy = []

    def set_values(self, range_for_slider, date, candles):

        self.candles = candles
        self.date = date

        self.slider_min = range_for_slider[0]
        self.slider_max = range_for_slider[1]
        self.slider_step = range_for_slider[2]

        self.slider_begin.setRange(self.slider_min, self.slider_max)
        self.slider_begin.setSingleStep(self.slider_step)
        self.slider_begin.setPageStep(self.slider_step)
        self.slider_begin.setValue(self.slider_min)

        self.slider_end.setRange(self.slider_min, self.slider_max)
        self.slider_end.setSingleStep(self.slider_step)
        self.slider_end.setPageStep(self.slider_step)
        self.slider_end.setValue(self.slider_max)

        self.begin_vLine.setValue(self.slider_min)
        # self.begin_vLine_USD.setValue(self.slider_min)
        # self.begin_vLine_BTC.setValue(self.slider_min)

        self.end_vLine.setValue(self.slider_max)

        self.data["begin_datetime"] = self.slider_min
        self.data["end_datetime"] = self.slider_max

        # calc last buy and sell prices
        min_date = datetime.datetime.utcfromtimestamp(self.slider_min)
        index_begin = np.where(self.date == min_date)[0][0]
        self.last_buy_price_test.setText( str(self.candles[index_begin] )[:8] )
        self.last_sell_price_test.setText( str(self.candles[index_begin] )[:8] )


        buy = float(self.last_sell_price_test.text()) - float(self.last_sell_price_test.text()) * (float(self.buy_threshold_test.text()) / 100)
        sell = float(self.last_buy_price_test.text()) + float(self.last_buy_price_test.text()) * (float(self.sell_threshold_test.text()) / 100)
        self.top_midway_hLine.setValue(sell)
        self.bottom_midway_hLine.setValue(buy)

        # self.top_midway_hLine.setBounds( (self.slider_min, None) )
        # self.bottom_midway_hLine.setBounds( (self.slider_min, None) )

    def value_dt_changed_begin(self, event):
        v = self.range_begin_dt.dateTime().toPyDateTime().replace(tzinfo=datetime.timezone.utc).timestamp() 
        if v < self.slider_min:
            v = self.slider_min
            v1 = datetime.datetime.utcfromtimestamp(v)
            self.range_begin_dt.setDateTime(v1)

        self.begin_vLine.setValue(v)
        self.begin_vLine_USD.setValue(v)
        self.begin_vLine_BTC.setValue(v)

        self.slider_begin.setValue(v)
        self.data["begin_datetime"] = v

        # calc last buy and sell prices
        min_date = datetime.datetime.utcfromtimestamp(v)
        index_begin = np.where(self.date <= min_date)[0][-1] 
        self.last_buy_price_test.setText( str(self.candles[index_begin] )[:8] )
        self.last_sell_price_test.setText( str(self.candles[index_begin] )[:8] )

        buy = float(self.last_sell_price_test.text()) - float(self.last_sell_price_test.text()) * (float(self.buy_threshold_test.text()) / 100)
        sell = float(self.last_buy_price_test.text()) + float(self.last_buy_price_test.text()) * (float(self.sell_threshold_test.text()) / 100)
        self.top_midway_hLine.setValue(sell)
        self.bottom_midway_hLine.setValue(buy)

        # self.top_midway_hLine.setBounds( (self.slider_min, None) )
        # self.bottom_midway_hLine.setBounds( (self.slider_min, None) )

    def value_dt_changed_end(self, event):
        v = self.range_end_dt.dateTime().toPyDateTime().replace(tzinfo=datetime.timezone.utc).timestamp() 
        if v > self.slider_max:
            v = self.slider_max
            v1 = datetime.datetime.utcfromtimestamp(v)
            self.range_end_dt.setDateTime(v1)

        self.end_vLine.setValue(v)
        self.slider_end.setValue(v)
        self.data["end_datetime"] = v

    def value_changed_begin(self, event):
        v = self.slider_begin.value()
        v1 = datetime.datetime.utcfromtimestamp(v)
        self.range_begin_dt.setDateTime(v1)
        self.begin_vLine.setValue(v)
        self.data["begin_datetime"] = v

        # calc last buy and sell prices
        min_date = datetime.datetime.utcfromtimestamp(v)
        index_begin = np.where(self.date <= min_date)[0][-1] 
        self.last_buy_price_test.setText( str(self.candles[index_begin] )[:8] )
        self.last_sell_price_test.setText( str(self.candles[index_begin] )[:8] )

        buy = float(self.last_sell_price_test.text()) - float(self.last_sell_price_test.text()) * (float(self.buy_threshold_test.text()) / 100)
        sell = float(self.last_buy_price_test.text()) + float(self.last_buy_price_test.text()) * (float(self.sell_threshold_test.text()) / 100)
        self.top_midway_hLine.setValue(sell)
        self.bottom_midway_hLine.setValue(buy)

        # self.top_midway_hLine.setBounds( (self.slider_min, None) )
        # self.bottom_midway_hLine.setBounds( (self.slider_min, None) )

    def value_changed_end(self, event):
        v = self.slider_end.value()
        v1 = datetime.datetime.utcfromtimestamp(v)
        self.range_end_dt.setDateTime(v1)
        self.end_vLine.setValue(v)
        self.data["end_datetime"] = v

    def on_click_plot(self, event):
        """
            Show text label with an information where user click
        """

        try:

            if event.currentItem is None:
                return None
            plot_sender = event.currentItem.parentItem()

            if len(self.plt_text_label) == 0:
                self.plt_text_label.update({
                    plot_sender: {"text": None, "arrow": None}
                    })

            if len(self.plt_text_label) > 0:
                if plot_sender not in self.plt_text_label.keys():
                    self.plt_text_label.update({
                        plot_sender: {"text": None, "arrow": None}
                        })
                else:
                    plot_sender.removeItem(self.plt_text_label[plot_sender]["text"])
                    plot_sender.removeItem(self.plt_text_label[plot_sender]["arrow"])
                    self.plt_text_label[plot_sender] = {"text": None, "arrow": None}

            if event.button() == 1:

                position = event.scenePos()
                x = plot_sender.vb.mapSceneToView(position).x()
                y = plot_sender.vb.mapSceneToView(position).y()

                r = plot_sender.vb.viewRange()
                if (x < r[0][0]) or (x > r[0][1]) or (y < r[1][0]) or (y > r[1][1]):
                    return None

                x_dt =  datetime.datetime.utcfromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")

                self.plt_text_label[plot_sender]["text"] = pg.TextItem(html='''
                                <div style="text-align: center; color: #FFF;  font-size: 9pt;">%s<br>%0.2f</div>''' % (x_dt, y) , 
                                anchor=(0.5,1.0))
                self.plt_text_label[plot_sender]["text"].setPos(x, y)
                # a1 = pg.ArrowItem(angle=-160, tipAngle=60, headLen=40, tailLen=40, tailWidth=20, pen={'color': 'w', 'width': 3})
                # a2 = pg.ArrowItem(angle=-120, tipAngle=30, baseAngle=20, headLen=40, tailLen=40, tailWidth=8, pen=None, brush='y')
                # a3 = pg.ArrowItem(angle=-60, tipAngle=30, baseAngle=20, headLen=40, tailLen=None, brush=None)
                # a4 = pg.ArrowItem(angle=-20, tipAngle=30, baseAngle=-30, headLen=40, tailLen=None)
                self.plt_text_label[plot_sender]["arrow"] = pg.ArrowItem(pos=(x, y), angle=-90, tipAngle=60, baseAngle=0, headLen=10, tailLen=None, brush=None)

                plot_sender.addItem(self.plt_text_label[plot_sender]["text"])
                plot_sender.addItem(self.plt_text_label[plot_sender]["arrow"])
        except Exception:
            return None

    def center(self, Form):
        """
            Centralize window
        """

        qr = Form.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        Form.move(qr.topLeft())

