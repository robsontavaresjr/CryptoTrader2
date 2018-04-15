
import datetime as dt
import numpy as np
import pandas as pds
import pandas_datareader.data as pd
import time
import requests
from BeautifulRequestData import *
############################################################################################################


class Data:

    def __init__(self, ticker, start, end, source='bitfinex', interval = '1h'):

        self.ticker = ticker
        self.start = start
        self.end = end
        self.interval = interval

        self.cryptoData =DataReader(self.ticker, self.start, self.end)

        if source == 'bitfinex':

            self.data = self.cryptoData.bitfinex()
            self.interval_gap = self.data.Date.diff()
            self.interval_gap.fillna(0, inplace=True)

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


class DatabaseBuilder:

    def __init__(self, tickerList, start_aq, end_aq, source='bitfinex'):

        self.database = {}
        self.tickerList = tickerList
        self.start = start_aq
        self.end = end_aq


        for eachTicker in self.tickerList:

            aq_ok = False

            ex_counter = 0

            while aq_ok == False:

                if ex_counter == 5:
                    raise Exception('Couldnt not acquire data for ' + str(eachTicker) + ' after 5 tries')

                try:

                    mydata = Data(eachTicker, self.start, self.end)
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

                        if eachIndicator == 'MMA':

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




start = dt.datetime(2018, 1, 1, 0, 0, 0)
end = dt.datetime(2018, 4, 14, 0, 0, 0)
ticker = 'ETHUSD'

db = DatabaseBuilder(['ETHUSD', 'BTCUSD'], start, end)
db.calculateIndicators(indicator_filter=['MMA', 'MME', 'LNR', 'TR'], period_filter=[7, 14, 21])