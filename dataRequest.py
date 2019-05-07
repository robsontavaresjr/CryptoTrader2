import time
import requests
import pandas as pds
import datetime as dt

class DataRequest:

    def __init__(self, ticker, start, end, interval='1h', source='bitfinex'):

        self.start = start
        self.end = end
        self.interval = interval
        self.ticker = ticker

        # Converting datetime to timestamp

        self.epoch = dt.datetime(1970, 1, 1)
        self.epochTS = self.epoch.timetuple()
        self.epochTS = time.mktime(self.epochTS)

        self.startTS = start
        self.startTS = self.startTS.timetuple()

        self.endTS = end
        self.endTS = self.endTS.timetuple()

        # Correcting for my timezone
        self.startTS = int(time.mktime(self.startTS) - self.epochTS) * 1000
        self.endTS = int(time.mktime(self.endTS) - self.epochTS) * 1000

        #Selecting Exchange (future enhancements are desired)
        #
        # if source == 'biftinex':
        #
        #     self.OHLC = self.bitfinex()

    def getFromBitfinex(self):

        # Structuring request's url
        ticker = self.ticker
        url = "https://api.bitfinex.com/v2/candles/trade:" + self.interval + ":t" + self.ticker + "/hist"
        response = requests.request("GET", url,
                                    params={'limit': 1000, 'start': int(self.startTS), 'end': int(self.endTS)})

        # handling data
        rawData = response.json()
        cryptoData = pds.DataFrame(rawData)

        #Renaming columns and transforming timestamp to datetime
        cryptoData.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']
        cryptoData['Date'] = cryptoData['Date'].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        cryptoData = cryptoData.sort_values("Date", ascending=True)

        return cryptoData

# Apenas para teste
if __name__ == "__main__":

    start = dt.datetime(2018, 1, 1, 0, 0, 0)
    end = dt.datetime(2018, 4, 14, 0, 0, 0)
    reader = DataRequest('ETHUSD', start, end)
    data = reader.getFromBitfinex()