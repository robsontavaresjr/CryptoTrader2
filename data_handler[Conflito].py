

import datetime        as dt
import numpy           as np
import pandas          as pds
import pandas.io.data  as pd
import cython

############################################################################################################


class Data:
    
    def __init__(self, ticker, start, end, source='google', workingdays=None):
        
        if type(start) == dt.datetime:
            self.start = start
        else:
            self.start = dt.datetime(*start)
            
        if type(end) == dt.datetime:
            self.end = end
        else:
            self.end = dt.datetime(*end)
            
        self.ticker = ticker
        self.source = source
        self.order = None

        stock_data = pd.DataReader(self.ticker, self.source, start=self.start, end=self.end)

        self.C = stock_data['Close']
        self.H = stock_data['High']
        self.L = stock_data['Low']
        self.V = stock_data['Volume']
        self.O = stock_data['Open']
        self.dates = map(lambda t: t.to_datetime(), stock_data.index)

        if workingdays is not None:

            workingday_str = map(lambda x: str(x.date()), workingdays)

            filtered_close = []
            filtered_high = []
            filtered_dates = []
            filtered_volume = []

            for dateindex in workingday_str:

                if dateindex in self.C.index:
                    filtered_close.append(self.C[dateindex])
                    filtered_high.append(self.H[dateindex])
                    filtered_volume.append(self.V[dateindex])
                    filtered_dates.append(workingdays[workingday_str.index(dateindex)])

            self.dates = filtered_dates
            self.C = pds.Series(filtered_close, index=self.dates)
            self.H = pds.Series(filtered_high, index=self.dates)
            self.V = pds.Series(filtered_volume, index=self.dates)



    def rsi_simples(self, order=14):

        # dif = self.C.diff()

        dif = self.ln_return()

        dUp, dDown = dif.copy(), dif.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0
        rolup = pds.rolling_mean(dUp, order)
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

        ups = diffs.copy()
        ups[ups < 0.0] = 0.0

        downs = diffs.copy()
        downs[downs > 0.0] = 0.0
        downs = abs(downs)

        #        MMUp = pds.rolling_mean(Ups,n)
        #        MMDown = pds.rolling_mean(Downs,n)

        mult = n - 1

        dUp = [0 for k in range(len(ups))]
        dDown = [0 for k in range(len(ups))]

        dUp[n] = (sum(ups[1:n + 1]) / n)
        dDown[n] = (sum(downs[1:n + 1]) / n)

        dates = self.dates

        for i in range(n + 1, len(dUp)):
            dUp[i] = (ups[i] + dUp[i - 1] * mult) / n
            dDown[i] = (downs[i] + dDown[i - 1] * mult) / n

        dUp = np.abs(np.array(dUp))
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

        x = self.C.copy()
        N = order
        alpha = 2. / (N + 1)

        y = []
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
        x = x[N:]

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


def database_builder(tickerList, start_aq, end_aq, source='google'):

    database = {}

    for eachTicker in tickerList:

        aq_ok = False

        ex_counter = 0

        while aq_ok == False:

            if ex_counter == 5:
                raise Exception('Couldnt not acquire data for ' + str(eachTicker) + ' after 5 tries')

            try:

                mydata = Data(eachTicker, start_aq, end_aq, source=source)
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


def VaR(slave, simulations=1000, risk = 0.05):

    import numpy.linalg as npa

    close = [np.array(slave.database[i]['CLOSE']) for i in range(slave.database.keys())]
    close = np.vstack(close).reshape([len(close), len(slave.database.keys())])
    dates = slave.database[i]['CLOSE'].index

    n = 100
    y = []

    for ctr in range(len(close), -1, -1):

        closeList = close[ctr - n:ctr]
        stocksLen = len(slave.database.keys())

        if len(closeList) == 0:
            break
        else:

            correlationMatrix = np.corrcoef(closeList.T)
            eigVal,eigVec     = npa.eig(correlationMatrix)

            portfolioVaR = []
            MCR          = []

            for iteration in range(simulations):

                pca = np.transpose(eigVec).dot(eigVal**0.5)
                pca = np.random.rand(n, stocksLen).dot(pca)

                MCR += pca.reshape([n*stocksLen, 1])

            MCR.sort()
            portfolioVaR.append(MCR[int(risk*(simulations*n*stocksLen))])
            del MCR

    # Para manter o tamanho!
    for i in range(n - 1):
        portfolioVaR.append(0.)

    portfolioVaR.reverse()

    return pds.Series(portfolioVaR, index = dates)

def calculate_indicators(tickerList, database,indicator_filter = []):

    indicators = {}
    working_days = {}
    indicator_strings = ['OPEN','HIGH','CLOSE',
                         'VOLUME','LNR','IFR',
                         'IFRS', 'MMA', 'STD',
                         'MME', 'HV', 'UBB',
                         'DBB', 'MMAD', 'MMAD2',
                         'SIGND2']

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
        
        periods = [2,7,50]

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
                            db_ind[indicator+'_'+ str(i)] = stock_data.rsi(i)
                    else:
                        db_ind[indicator + '_' + str(order)] = stock_data.rsi(order)

                if indicator == 'IFRS':

                    if order == 'all':
                        for i in periods:
                            db_ind[indicator + '_' + str(i)] = stock_data.rsi_simples(i)
                    else:
                        db_ind[indicator + '_' + str(order)] = stock_data.rsi_simples(order)

                if indicator in ('MMA','STD','MMAD','MMAD2','SIGNMMAD2','UBB','DBB'):

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

                        mma,std = stock_data.mma(order)

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

        indicators[eachTicker] = db_ind
        working_days[eachTicker] = stock_data.dates

    return indicators, working_days


############################################################################################################


def workmemory_feeder(wm, slave, current_date):

    for eachTicker in slave.portfolio.keys():

        if current_date in slave.wd[eachTicker]:

            daystr = str(current_date.date())

            prev_day = slave.wd[eachTicker][slave.wd[eachTicker].index(current_date) - 1]

            prev_daystr = str(prev_day.date())

            two_prev_day = slave.wd[eachTicker][slave.wd[eachTicker].index(current_date) - 2]
            two_prev_daystr = str(two_prev_day.date())

            feeder = slave.database[eachTicker]

            for eachKey in feeder.keys():
                wm[eachTicker][eachKey] = feeder[eachKey][daystr]

            wm[eachTicker]['HIGHM2'] = max(feeder['HIGH'][prev_daystr], feeder['HIGH'][two_prev_daystr])
            wm[eachTicker]['CLOSEM2'] = max(feeder['CLOSE'][prev_daystr], feeder['CLOSE'][two_prev_daystr])
            wm[eachTicker]['BUY'] = None
            wm[eachTicker]['SELL'] = None
            wm[eachTicker]['LAST_OP'] = None
            wm[eachTicker]['PRICE'] = feeder['CLOSE'][daystr]
#            wm[eachTicker]['MMA7'] = feeder['MMA7'][daystr]
            wm[eachTicker]['LAST_CLOSE'] = feeder['CLOSE'][prev_daystr]
#            wm[eachTicker]['LAST_MMA9'] = feeder['MMA9'][prev_daystr]
            
#            wm[eachTicker]['LAST_MMA_D_9'] = feeder['MMA_D_9'][prev_daystr]
#            wm[eachTicker]['LAST_MMA_D2_9'] = feeder['MMA_D2_9'][prev_daystr]            
#            wm[eachTicker]['LAST_SIGN_D2_9'] = feeder['SIGN_D2_9'][prev_daystr]
            
#            wm[eachTicker]['LAST_MMA11'] = feeder['MMA11'][prev_daystr]
#            wm[eachTicker]['LAST_MMA7'] = feeder['MMA7'][prev_daystr]
#            wm[eachTicker]['LAST_MMA3'] = feeder['MMA3'][prev_daystr]
            wm[eachTicker]['INVALID_DATE'] = False

            # Checking for data validity

            for eachKey in wm[eachTicker].keys():

                if repr(wm[eachTicker][eachKey]) == 'nan':
                    wm[eachTicker]['INVALID_DATE'] = True

        else:

            feeder = slave.database[eachTicker]

            wm[eachTicker]['INVALID_DATE'] = True

    return wm


############################################################################################################    
if __name__ == '__main__':
    #data = Data('CIEL3', (2015, 1, 1), (2016, 4, 20), source='google')  # ,WorkingDays = WorkingDays)

    db = database_builder(['PETR3','ABEV3'],(2015,1,1),(2016,1,1))

    ind,wd = calculate_indicators(['PETR3','ABEV3'],db,indicator_filter = ['C_MMA_9','C_HV_5','C_IFR_2'])
    ############################################################################################################