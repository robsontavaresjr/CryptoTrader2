# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 10:13:02 2016

@author: Suporte
"""
import datetime as dt
import numpy as np
import pandas as pds
import pandas.io.data as pd
import IntraDay

class Data_ID:
    
    def __init__(self, ticker, interval, daysBack, workingdays=None):

        self.order = None #O que é ???

        self.interval = interval
        self.daysBack = daysBack
        self.ticker = ticker

        stock_data = IntraDay.IntraDay_Acquisition(self.ticker,self.interval,self.daysBack)
        
        self.O = stock_data.O
        self.H = stock_data.H        
        self.L = stock_data.L        
        self.C = stock_data.C
        
        self.V = stock_data.V
        
        self.dates = stock_data.dates

    def rsi_simples(self, order=14):

        # dif = self.C.diff()

        dif = self.ln_return()

        dUp, dDown       = dif.copy(), dif.copy()
        dUp[dUp < 0]     = 0
        dDown[dDown > 0] = 0
        
        rolup   = pds.rolling_mean(dUp, order)
        roldown = pds.rolling_mean(dDown, order).abs()

        # RolUp = pds.stats.moments.ewma(dUp, com = order)
        # RolDown = pds.stats.moments.ewma(dDown, com = order)

        rs = rolup / roldown

        rsi = 100 - (100 / (1 + rs))

        for i in range(len(rsi)):

            if repr(rsi[i]) == 'nan':
                
                rsi[i] = 100.

        return rsi

    def ln_return(self):

        ln_r = []

        serie = map(lambda x: float(x), self.C)

        for i in range(len(serie)):

            try:

                if serie[i - 1] == 0.:
                    r = 0.0
                elif serie[i] == 0.:
                    r = 0.0
                else:
                    r = np.log(serie[i] / serie[i - 1])

            except ValueError:

                print serie[i]
                print serie[i - 1]

                raise Exception("Valor invalido para log.")

            ln_r.append(r)

        Dates = self.dates
        return pds.Series(ln_r, index=Dates)

    def rsi(self, n):

        p_series = self.C.copy()

        diffs = p_series.diff()

        #        diffs = self.ln_return()

        ups            = diffs.copy()
        ups[ups < 0.0] = 0.0

        downs              = diffs.copy()
        downs[downs > 0.0] = 0.0
        downs              = abs(downs)

        #        MMUp = pds.rolling_mean(Ups,n)
        #        MMDown = pds.rolling_mean(Downs,n)

        mult = n - 1

        dUp   = [0 for k in range(len(ups))]
        dDown = [0 for k in range(len(ups))]

        dUp[n]   = (sum(ups[1:n + 1]) / n)
        dDown[n] = (sum(downs[1:n + 1]) / n)

        dates = self.dates

        for i in range(n + 1, len(dUp)):
            
            dUp[i]   = (ups[i] + dUp[i - 1] * mult) / n
            dDown[i] = (downs[i] + dDown[i - 1] * mult) / n

        dUp   = np.abs(np.array(dUp))
        dDown = np.abs(np.array(dDown))

        rs = dUp / dDown

        rsi = (100 - (100 / (1 + rs)))

        for i in range(len(rsi)):

            if repr(rsi[i]) == 'nan':
              
              rsi[i] = 0.

        return pds.Series(rsi, index=dates)

    def mma(self, order=7):

        ''' Funcao que calcula a media movel e desvio padrao para N termos de uma serie '''

        x = self.C.copy()
        n = order

        y = []
        stdlist = []

        for ctr in range(len(x), -1, -1):

            xlist = x[ctr - n:ctr]

            if len(xlist) == 0:
                break
            else:
                y.append(sum(xlist) / n)
                stdlist.append(np.std(xlist))

        # Para manter o tamanho!
        for i in range(order - 1):
            y.append(0.)
            stdlist.append(0.)

        y.reverse()
        stdlist.reverse()

        return pds.Series(y, index=self.dates), pds.Series(stdlist, index=self.dates)

    def mme(self, order=7):

        ''' Funcao que calcula a media movel e desvio padrao para N termos de uma serie '''

        x     = self.C.copy()
        N     = order
        alpha = 2. / (N + 1)

        y       = []
        stdlist = []
        
        for ctr in range(len(x), -1, -1):

            xlist = x[ctr - N:ctr]

            if len(xlist) == 0:
                break
            else:
                y.append(sum(xlist) / N)
                stdlist.append(np.std(xlist))

        # Para manter o tamanho!
        for i in range(order - 1):

            y.append(0.)
            stdlist.append(0.)

        y.reverse()
        stdlist.reverse()

        mma = y[N - 1]
        mme = [mma]
        x   = x[N:]

        for i in range(len(y[N:])):
            
            mme.append(mme[-1] + (x[i] - mme[-1]) * alpha)

        mme = [0 for i in range(N - 1)] + mme

        return pds.Series(mme, index=self.dates)

    def hv(self, order=14):

        c = self.C.copy()

        for i in range(len(c) - 1, 0, -1):

            c[i] = c[i] / c[i - 1]

        c = np.log(c)

        mma, std = self.mma_from_series(c, order)

        return std * (252 ** 0.5)

    def mma_from_series(self, x, order=14):

        ''' Funcao que calcula a media movel e desvio padrao para N termos de uma serie '''

        n = order

        y       = []
        stdlist = []

        for ctr in range(len(x), -1, -1):

            xlist = x[ctr - n:ctr]

            if len(xlist) == 0:
                
                break

            else:

                y.append(sum(xlist) / n)
                stdlist.append(np.std(xlist))

        # Para manter o tamanho!
        for i in range(order - 1):

            y.append(0.)
            stdlist.append(0.)

        y.reverse()
        stdlist.reverse()

        return pds.Series(y, index=self.dates), pds.Series(stdlist, index=self.dates)

    def true_range(self):

        c = self.C.copy()
        h = self.H.copy()
        l = self.L.copy()

        p1 = list(h - l)

        p2 = [0.]
        p3 = [0.]
        for i in range(1,len(c)):
            p2.append(abs(h[i] - c[i-1]))
            p3.append(abs(l[i] - c[i-1]))

        TR = []
        for i in range(len(c)):
            m = max(p1[i],p2[i],p3[i])
            TR.append(m)

        return pds.Series(TR,index = c.index)

    def average_true_range(self,order = 14):

        atr = [0. for k in range(order)]

        TR = self.true_range()

        first_atr = np.mean(TR[0:order])

        atr.append(first_atr)

        for i in range(order+1,len(TR)):

            c_atr = ((atr[i-1] * (order-1)) + TR[i])/order
            atr.append(c_atr)

        return pds.Series(atr,index = TR.index)







def database_builder(tickerList, interval, daysBack, source='google'):

    database = {}

    for eachTicker in tickerList:

        aq_ok = False

        ex_counter = 0

        while aq_ok == False:

            if ex_counter == 5:
                raise Exception('Couldnt not acquire data for ' + str(eachTicker) + ' after 5 tries')

            try:

                mydata = Data_ID(eachTicker, interval, daysBack)
                database[eachTicker] = mydata
                aq_ok = True

                print eachTicker, 'ok.'

            except Exception as E:

                print E.message
                print 'Trying again ... '
                ex_counter += 1

    return database


def database_loader(location):

    import pickle

    arq = open(location, 'r')

    db = pickle.load(arq)

    arq.close()

    return db


def workmemory_builder(tickerList):

    wm = {}

    for eachTicker in tickerList:
        eachTicker = eachTicker.upper()
        wm[eachTicker] = {}

    return wm


def calculate_indicators(tickerList, database,indicator_filter = []):

    indicators = {}
    working_days = {}
    indicator_strings = ['OPEN','HIGH','CLOSE','LOW',
                         'VOLUME','LNR','IFR',
                         'IFRS', 'MMA', 'STD',
                         'MME', 'HV', 'UBB',
                         'DBB', 'MMAD', 'MMAD2',
                         'SIGND2','TR','ATR']

    if indicator_filter == []:
        filter_ = zip(indicator_strings,['all']*len(indicator_strings))
    else:
        filter_ = []
        for eachindicator in indicator_filter:
            tokens = eachindicator.split('_')
            if len(tokens) == 3:
                t,i,o = tokens
                o = int(o)
            elif len(tokens) == 2:
                t,i = tokens
                o = 0
            else:
                i = tokens[0]
                o = 0
            if i in indicator_strings:
                filter_.append([i,o])

    for eachTicker in tickerList:

        db_ind = {}

        stock_data = database[eachTicker]
        
        periods = [2,3,5,7,8,9,10,14,20,50,200]

        for ind_ord in filter_:

            indicator = ind_ord[0]
            order = ind_ord[1]

            in_db = []

            if order != "all":
                in_db.append(indicator + '_' + str(order) in db_ind.keys())

            else:
                for i in periods:
                    in_db.append(indicator + '_' + str(i) in db_ind.keys())

            if not all(in_db):

                if indicator == 'IFR':

                    if order == 'all':
                        for i in periods:
                            db_ind[indicator+'_' + str(i)] = stock_data.rsi(i)
                    else:
                        db_ind[indicator + '_' + str(order)] = stock_data.rsi(order)

                if indicator == 'IFRS':

                    if order == 'all':
                        for i in periods:
                            db_ind[indicator + '_' + str(i)] = stock_data.rsi_simples(i)
                    else:
                        db_ind[indicator + '_' + str(order)] = stock_data.rsi_simples(order)

                if indicator in ('MMA', 'STD', 'MMAD', 'MMAD2', 'SIGNMMAD2', 'UBB', 'DBB'):

                    if order == 'all':
                        for i in periods:

                            mma,std = stock_data.mma(i)

                            db_ind['MMA_' + str(i)] = mma
                            db_ind['STD_' + str(i)] = std
                            db_ind['UBB' + '_' + str(i)] = mma + 2. * std
                            db_ind['DBB' + '_' + str(i)] = mma - 2. * std

                            md = mma.diff()
                            md2 = md.diff()
                            md2sign = np.sign(md2)

                            db_ind['MMAD' + '_' + str(i)] = md
                            db_ind['MMAD2' + '_' + str(i)] = md2
                            db_ind['SIGNMMAD2' + '_' + str(i)] = md2sign
                    else:

                        mma, std = stock_data.mma(order)

                        if indicator in ('MMA','STD'):

                            db_ind['MMA' + '_' + str(order)] = mma
                            db_ind['STD' + '_' + str(order)] = std

                        if indicator in ('UBB','DBB'):

                            db_ind['UBB' + '_' + str(order)] = mma + 2.*std
                            db_ind['DBB' + '_' + str(order)] = mma - 2.*std

                        if indicator in  ('MMAD','MMAD2','SIGNMMAD2'):

                            md = mma.diff()
                            md2 = md.diff()
                            md2sign = np.sign(md2)

                            db_ind['MMAD' + '_' + str(order)] = md
                            db_ind['MMAD2' + '_' + str(order)] = md2
                            db_ind['SIGNMMAD2' + '_' + str(order)] = md2sign

                if indicator == 'MME':

                    if order == 'all':
                        for i in periods:
                            db_ind[indicator + '_' + str(i)] = stock_data.mme(i)
                    else:
                        db_ind[indicator + '_' + str(order)] = stock_data.mme(order)

                if indicator == 'HV':

                    if order == 'all':
                        for i in periods:
                            db_ind[indicator + '_' + str(i)] = stock_data.hv(i)
                    else:
                        db_ind[indicator + '_' + str(order)] = stock_data.hv(order)

                if indicator == 'ATR':

                    if order == 'all':
                        for i in periods:
                            db_ind[indicator + '_' + str(i)] = stock_data.average_true_range(i)
                    else:
                        db_ind[indicator + '_' + str(order)] = stock_data.average_true_range(order)

                if indicator == 'OPEN':

                    db_ind[indicator] = stock_data.O

                if indicator == 'HIGH':

                    db_ind[indicator] = stock_data.H

                if indicator == 'LOW':

                    db_ind[indicator] = stock_data.L

                if indicator == 'CLOSE':

                    db_ind[indicator] = stock_data.C

                if indicator == 'VOLUME':

                    db_ind[indicator] = stock_data.V

                if indicator == 'LNR':

                    db_ind[indicator] = stock_data.ln_return()

                if indicator == 'TR':

                    db_ind[indicator] = stock_data.true_range()

        db_ind['CLOSE'] = stock_data.C
        indicators[eachTicker] = db_ind
        working_days[eachTicker] = stock_data.dates

    return indicators, working_days


############################################################################################################


def workmemory_feeder(wm, slave, current_date, indicator_filter = []):

    period_indicator = []

    for indicator in indicator_filter:

        tokens = indicator.split('_')

        if len(tokens) == 1:

            period_indicator.append(tokens[0])

        elif len(tokens) == 2:

            if tokens[0] == 'C':
                index = 0
            else:
                index = int(tokens[0][1:])

            period_indicator.append([index,tokens[0],tokens[1]])

        elif len(tokens) == 3:

            if tokens[0] == 'C':
                index = 0
            else:
                index = int(tokens[0][1:])

            period_indicator.append([index,tokens[0],tokens[1]+'_'+tokens[2]])


    for eachTicker in slave.portfolio.keys():

        feeder = slave.database[eachTicker]

        if current_date in slave.wd[eachTicker]:

            daystr = str(current_date)

            prev_day = slave.wd[eachTicker][slave.wd[eachTicker].index(current_date) - 1]

            prev_daystr = str(prev_day)

            two_prev_day = slave.wd[eachTicker][slave.wd[eachTicker].index(current_date) - 2]
            two_prev_daystr = str(two_prev_day)

            if indicator_filter !=[]:

                for key in period_indicator:

                    if type(key) == str:

                        wm[eachTicker][key] = feeder[key][daystr]

                    elif type(key) == list:

                        index = key[0]
                        wmkey = key[1]+'_'+key[2]

                        n_day = slave.wd[eachTicker][slave.wd[eachTicker].index(current_date) - index]
                        n_day_str = str(n_day.date())

                        wm[eachTicker][wmkey] = feeder[key[2]][n_day_str]

            else:

                for eachKey in feeder.keys():
                    wm[eachTicker][eachKey] = feeder[eachKey][daystr]

                    wm[eachTicker]['L1_OPEN'] = feeder['OPEN'][prev_daystr]
                    wm[eachTicker]['L2_OPEN'] = feeder['OPEN'][two_prev_daystr]

                    wm[eachTicker]['L1_CLOSE'] = feeder['CLOSE'][prev_daystr]
                    wm[eachTicker]['L2_CLOSE'] = feeder['CLOSE'][two_prev_daystr]

                if 'HIGH' in feeder.keys():
    #                wm[eachTicker]['HIGHM2'] = max(feeder['HIGH'][prev_daystr], feeder['HIGH'][two_prev_daystr])
                    wm[eachTicker]['HIGHM2'] = max(feeder['HIGH'][daystr], feeder['HIGH'][prev_daystr])
                    wm[eachTicker]['LOWM2'] = min(feeder['LOW'][daystr], feeder['LOW'][prev_daystr])
                if 'CLOSE' in feeder.keys():
    #                wm[eachTicker]['CLOSEM2'] = max(feeder['CLOSE'][prev_daystr], feeder['CLOSE'][two_prev_daystr])
                    wm[eachTicker]['CLOSEM2'] = max(feeder['CLOSE'][daystr], feeder['CLOSE'][prev_daystr])

                wm[eachTicker]['BUY'] = None
                wm[eachTicker]['SELL'] = None
                wm[eachTicker]['LAST_OP'] = None
                wm[eachTicker]['PRICE'] = feeder['CLOSE'][daystr]
                wm[eachTicker]['INVALID_DATE'] = False

            # Checking for data validity

            for eachKey in wm[eachTicker].keys():

                if repr(wm[eachTicker][eachKey]) == 'nan':
                    wm[eachTicker]['INVALID_DATE'] = True

        else:

            feeder = slave.database[eachTicker]

            wm[eachTicker]['INVALID_DATE'] = True

    return wm


# ############################################################################################################
# if __name__ == '__main__':
#     #data = Data('CIEL3', (2015, 1, 1), (2016, 4, 20), source='google')  # ,WorkingDays = WorkingDays)
#
#     db = database_builder(['PETR3','ABEV3'],300,5)
#
#     ind,wd = calculate_indicators(['PETR3','ABEV3'],db,indicator_filter = ['LAST_MMA_9','C_HV_5','C_IFR_2','C_VOLUME'])
#     ############################################################################################################