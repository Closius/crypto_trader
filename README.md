# Crypto Trader

For automatic trading on the stock exchange.
Current implementation is for cryptocurrency trading on
the cryptocurrency stock exchange Bitfinex.

**Features:**
Web based.
Server side: trading, collecting and storing history data, http server.
Frontend: GUI, remote management, test strategy.

**Owerview:**
Current implementation developed for cryptocurrency trading on
the cryptocurrency stock exchange [Bitfinex](https://www.bitfinex.com).
You have to have account and [API Access](https://docs.bitfinex.com/docs/api-access).

## Installation:

### Server (Ubuntu 16.04):

Connect to your server. You can do it with following command:
```
ssh root@111.222.333.444 -p 22
```

Create user, update packages, clone repo:
```
adduser --gecos "" crypto_trader
usermod -aG sudo crypto_trader
apt-get -y update
apt-get -y upgrade
apt-get -y install git nano
su - crypto_trader
git clone https://github.com/Closius/crypto_trader.git
cd crypto_trader
```

I recommend to set your own ``POSTGRES_PASSWORD`` and ``TRADER_PASSWORD`` in ``setup.sh`` for PostgresSql database
(With ``setup.sh`` PostgresSql will be installed and a new database will be created).
Set your values in ``server/secret_settings.py``
Hint: press Ctrl+X to finish editing with nano.
```
chmod +rx setup.sh
nano setup.sh
nano server/secret_settings.py
```

Run setup script:
```
sudo bash setup.sh
```

### Frontend (tested on MacOs and Windows 7, 10):

```
git clone https://github.com/Closius/crypto_trader.git
```

Install [Anaconda](https://www.anaconda.com/download). I use Python 3.5.2 :: Anaconda 4.2.0 (x86_64)
From Anaconda you need:
```
requests
matplotlib
statsmodels
PyQt5 (I use 5.10)
numpy
```

Install PyQtGraph

```
pip install pyqtgraph
```

Install [TA-lib](https://github.com/mrjbq7/ta-lib#dependencies).
For Windows you can try [unofficial windows binaries for both 32-bit and 64-bit](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)


Set ``SERVER_ENDPOINT`` in ``secret_settings.py``

## Get started:

1. Install
2. Run GUI: ``python trader/monitor_test.py``
3. Start the data collecting.
    Go to the last Tab and add pairs and timeframes.
    Start Collector
    The history data will be collected for this pairs and timeframes.
    Note: You can trade only with pairs and timeframes that you've added.
4. Ensure that the data collecting has been started by pushing the "Info" button.
    Note: You should wait a while. Check "count" for pairs, it should more than 200.
5. You can play testing strategy before trading on testing tab
6. Start trading. Go to the trading tab. Enter parameters and push Start button.

