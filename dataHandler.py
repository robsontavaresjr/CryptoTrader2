
import datetime as dt
import numpy as np
import pandas as pds
import pandas_datareader.data as pd
import time
import requests
from dataRequest import DataRequest
############################################################################################################


class DataHandler(DataRequest):

    def __init__(self, ticker, start, end, source='bitfinex', interval = '1h'):

        self.ticker = ticker
        self.start = start
        self.end = end
        self.interval = interval

        DataRequest.__init__(self, ticker, start, end, interval=interval, source=source)

        if source == 'bitfinex':

            self.data = self.getFromBitfinex()
            self.interval_gap = self.data.Date.diff()
            self.interval_gap.fillna(0, inplace=True)

        else:
            raise Exception("Source {0} not implemented.".format(source))

    #Standard log return of closing price
    def ln_return(self):

        data = self.data.copy()
        data['Interval'] = self.interval_gap

        data['LN_RETURN'] = data.Close.divide(
                            data.Close.shift(1), fill_value=0)

        data['LN_RETURN'] = data['LN_RETURN'].apply(
                                lambda x: np.log(x))

        return data[['Date', 'Interval', 'Close', 'LN_RETURN']]

    #Standard moving average and its standdard deviation, on desired window, of closing price
    def mma(self, order = 7):

        data = self.data.copy()
        data['Interval'] = self.interval_gap

        data['MMA'] = data.Close.rolling(order, min_periods=order).mean()
        data['MMA'].fillna(0, inplace=True)

        data['MMA_STD'] = data.Close.rolling(order, min_periods=order).std()
        data['MMA_STD'].fillna(0, inplace=True)

        data['UBB'] = data.MMA.values + 2 * data.MMA_STD.values
        data['DBB'] = data.MMA.values - 2 * data.MMA_STD.values

        return data[['Date', 'Interval', 'Close', 'MMA', 'MMA_STD', 'UBB', 'DBB']]

    # Exponential moving average and its standdard deviation, on desired window, of closing price
    def mme(self, order=7):

        data = self.data.copy()
        data['Interval'] = self.interval_gap

        data['MME'] = data.Close.ewm(span=order).mean()
        data['MME'].fillna(0, inplace=True)

        data['MME_STD'] = data.Close.ewm(span=order).std()
        data['MME_STD'].fillna(0, inplace=True)

        data['UBB'] = data.MME.values + 2 * data.MME_STD.values
        data['DBB'] = data.MME.values - 2 * data.MME_STD.values

        return data[['Date', 'Interval', 'Close', 'MME', 'MME_STD']]

    def hv(self, order=7):

        data = self.data.copy()
        data['Interval'] = self.interval_gap

        data['HV']= data.Close.divide(
            data.Close.shift(1, fill_value=0))

        data['HV'] = data.HV.apply(lambda x: np.log(x))
        data['HV'] = data.HV.rolling(order, min_periods=order).std()
        data['HV'] = data.HV.apply(lambda x: x * (252*0.5))

        return data[['Date', 'Interval', 'Close', 'HV']]

    def true_range(self):

        data = self.data.copy()
        data['Interval'] = self.interval_gap

        data['p1'] = data['High'].values  - data['Low'].values

        data['p2'] = data['High'].values  - data['Close'].shift(1).values
        data.p2 = data.p2.abs()

        data['p3'] = data.Low.values - data.Close.shift(1).values
        data.p3 = data.p3.abs()

        data.loc[data.index == 0, ['p1', 'p2', 'p3']] = 0.

        data['TRUE_RANGE'] = data[['p1', 'p2', 'p3']].max(axis=1)


        return data[['Date', 'Interval', 'Close', 'TRUE_RANGE']]

    def average_true_range(self, order=14):

        data = self.data.copy()
        data['Interval'] = self.interval
        tr = self.true_range()['TRUE_RANGE']

        atr = tr.ewm(span=order).mean()

        return data[['Date', 'Interval', 'Close', 'AVG_TRUE_RANGE']]

    def rsi_simples(self, order=14):

        data = self.data.copy()
        data['Interval'] = self.interval
        incremental = 1

        data['Diff'] = data.Close.diff()
        data['Diff'].fillna(0, inplace=True)

        data['Ups'] = data.Diff
        data['Downs'] = data.Diff

        data.Ups.loc[data.Ups < 0] = 0.
        data.Downs.loc[data.Diff > 0] = 0.
        data.Downs = data.Downs.apply(lambda x: abs(x))

        data.Ups = data.Ups.rolling(order, min_periods=order).mean()
        data.Ups.fillna(0, inplace=True)

        data.Downs = data.Downs.rolling(order, min_periods=order).mean()
        data.Downs.fillna(0, inplace=True)
        # data.Downs.loc[data.Downs == 0] = 1

        data['RSI'] = 100. - (100. / (1. + (data.Ups.values / data.Downs.values)))
        data['RSI'].fillna(0, inplace=True)

        return data[['Date', 'Interval', 'Close', 'RSI']]


    def rsi(self, order=7):

        data = self.data.copy()
        data['Interval'] = self.interval

        data['Diff'] = data.Close.diff()
        data['Diff'].fillna(0, inplace=True)

        data['Ups'] = data.Diff
        data['Downs'] = data.Diff

        data.Ups.loc[data.Ups < 0] = 0.
        data.Downs.loc[data.Diff > 0] = 0.
        data.Downs = data.Downs.apply(lambda x: abs(x))

        mult = (order-1)/float(order)

        data.Ups = data.Ups.ewm(span=order).mean()
        data.Ups.fillna(0, inplace=True)

        data.Downs = data.Downs.ewm(span=order).mean()
        data.Downs.fillna(0, inplace=True)
        data.Downs.loc[data.Downs == 0] = 1

        data['RSI'] = 100. - (100./(1. +(data.Ups.values/data.Downs.values)))
        data['RSI'].fillna(0, inplace=True)

        return data[['Date', 'Interval', 'Close', 'RSI']]


class DatabaseBuilder:

    def __init__(self, tickerList, start_aq, end_aq, source):

        self.database = {}
        self.tickerList = tickerList
        self.start = start_aq
        self.end = end_aq

        for eachTicker in self.tickerList:

            aq_ok = False
            ex_counter = 0

            while not aq_ok:

                if ex_counter == 5:
                    raise Exception('Couldnt not acquire data for ' + str(eachTicker) + ' after 5 tries')

                try:

                    mydata = DataHandler(eachTicker, self.start, self.end, source=source)
                    self.database[eachTicker] = mydata
                    aq_ok = True

                    print eachTicker, 'ok.'

                except Exception as E:

                    print E.message
                    print 'Trying again ... '
                    ex_counter += 1

    def calculateIndicators(self, indicator_filter=[], period_filter=[]):

        indicators = {}
        periodic_indicators = ['IFR', 'IFRS', 'MMA', 'STD',
                             'HV', 'UBB', 'DBB', 'MMAD', 'MMAD2', 'ATR']

        for eachTicker in self.database.keys():
            db_ind = self.database[eachTicker].data.copy()
            for eachIndicator in indicator_filter:
                if eachIndicator in periodic_indicators:

                    for eachPeriod in period_filter:

                        if eachIndicator == 'IFRS':

                            db_ind['IFRS_' + str(eachPeriod)] = \
                                self.database[eachTicker].rsi_simples(order=eachPeriod)['RSI']

                        elif eachIndicator == 'IFR':

                            db_ind['IFR_' + str(eachPeriod)] = \
                                self.database[eachTicker].rsi(order=eachPeriod)['RSI']

                        elif eachIndicator == 'ATR':
                            db_ind['ATR_' + str(eachPeriod)] = \
                                self.database[eachTicker].average_true_range(order=eachPeriod)['AVG_TRUE_RANGE']

                        elif eachIndicator == 'MMA':

                            db_ind['MMA_' + str(eachPeriod)] = \
                                self.database[eachTicker].mma(order=eachPeriod)['MMA'].values
                            db_ind['MMA_STD_' + str(eachPeriod)] = \
                                self.database[eachTicker].mma(order=eachPeriod)['MMA_STD'].values
                            db_ind['UBB_' + str(eachPeriod)] = \
                                self.database[eachTicker].mma(order=eachPeriod)['UBB'].values
                            db_ind['DBB_' + str(eachPeriod)] = \
                                self.database[eachTicker].mma(order=eachPeriod)['DBB'].values

                        elif eachIndicator == 'MME':
                            db_ind['MME_' + str(eachPeriod)] = \
                                self.database[eachTicker].mme(order=eachPeriod)['MME'].values
                            db_ind['MME_STD_' + str(eachPeriod)] = \
                                self.database[eachTicker].mme(order=eachPeriod)['MME_STD'].values
                            db_ind['MME_UBB_' + str(eachPeriod)] = \
                                self.database[eachTicker].mme(order=eachPeriod)['UBB'].values
                            db_ind['MME_DBB_' + str(eachPeriod)] = \
                                self.database[eachTicker].mme(order=eachPeriod)['DBB'].values

                else:
                    db_ind['LNR'] = self.database[eachTicker].ln_return()['LN_RETURN']
                    db_ind['TR'] = self.database[eachTicker].true_range()['TRUE_RANGE']

            indicators[eachTicker] = db_ind

        return indicators

def workmemoryFeeder(indicators, date):

    wm = {key : {} for key in indicators.keys()}
    for ticker in indicators.keys():
        data = indicators[ticker][indicators[ticker]["Date"].isin([date])]
        data.columns = map(lambda name : name.upper(), data.columns)
        if len(data) == 1:
            dataDict = data.to_dict(orient="list")
            for key in dataDict.keys():
                dataDict[key] = dataDict[key][0]
            wm[ticker] = dataDict
            wm[ticker]["INVALID_DATE"] = False
            wm[ticker]["PRICE"] = wm[ticker]["CLOSE"]
        else:
            wm[ticker]["INVALID_DATE"] = True

        wm[ticker]["LAST_OP"] = None
        wm[ticker]["BUY"] = None
        wm[ticker]["SELL"] = None
    return wm

if __name__ == "__main__":
    start = dt.datetime(2018, 1, 1, 0, 0, 0)
    end = dt.datetime(2018, 4, 14, 0, 0, 0)
    ticker = 'ETHUSD'
    db = DatabaseBuilder(['ETHUSD', 'BTCUSD'], start, end, source="bitfinex")
    data = db.calculateIndicators(indicator_filter=['MMA', 'MME', 'LNR', 'TR'], period_filter=[7, 14, 21])
    A = db.calculateIndicators(indicator_filter=['MMA', 'MME', 'LNR', 'TR', 'IFR'], period_filter=[7, 14, 21])
