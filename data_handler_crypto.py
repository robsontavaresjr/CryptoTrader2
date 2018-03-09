import requests
import datetime as dt
import pandas as pd
import time

class Data:

    def __init__(self, ticker, start, end, interval='1D'):

        self.interval = interval

        #Converting datetime to timestamp

        self.epoch = dt.datetime(1970, 1, 1)
        self.epochTS = self.epoch.timetuple()
        self.epochTS = time.mktime(self.epochTS)

        self.startTS = start
        self.startTS = self.startTS.timetuple()
        #Correcting for my timezone
        self.startTS = int(time.mktime(self.startTS) - self.epochTS) * 1000

        self.endTS = end
        self.endTS = self.endTS.timetuple()
        self.endTS = int(time.mktime(self.endTS) - self.epochTS) * 1000

        #Structuring request's url
        self.ticker = ticker
        self.url = "https://api.bitfinex.com/v2/candles/trade:" + self.interval + ":t" + self.ticker + "/hist"
        response = requests.request("GET", self.url, params={'limit': 1000, 'start': int(self.startTS), 'end': int(self.endTS)})


        #handling data
        self.rawData = response.json()
        self.cryptoData = pd.DataFrame(self.rawData, columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        self.cryptoData['Time'] = self.cryptoData['Time'].apply(lambda x: dt.datetime.fromtimestamp(x/1000))

        # self.C = self.cryptoData['Close']
        # self.H = self.cryptoData['High']
        # self.L = self.cryptoData['Low']
        # self.V = self.cryptoData['Volume']
        # self.O = self.cryptoData['Open']
data = Data('BTCUSD', dt.datetime(2018, 1, 1), dt.datetime(2018, 3, 1))