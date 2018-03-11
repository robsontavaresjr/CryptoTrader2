# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 09:41:30 2015

@author: Aluno - Joao
"""
import tradex
import datetime as dt
import copy
import risklib
import math
import pandas
import numpy as np
import random


######################################################

# Class that defines Trader entity

class SlaveTrader:
    def __init__(self, strategy, working_days, initcash, database):

        ######################################################

        # Strategy - Rule

        self.strategy = strategy[1]
        self.strategy_variables = strategy[0]

        ######################################################

        # Risk Weights

        self.risk_weights = {}

        # Current cash - Initial allocated cash

        # CASH IS A DICTIONARY TICKER:AMMOUNT
        self.cash = initcash
        self.total_initcash = initcash

        ######################################################

        # Operation log - dictionary 
        # FORMAT -> TICKER: [{},{},{}, ... ] - list of dictionaries with relevant information about all operations

        self.operation_log = {}

        ######################################################

        # Portfolio - dictionary
        # FORMAT -> TICKER: [[DATE,STOCKS,BOUGHT_PRICE],[...],[...],...] - list of lists with information about stock operation date, number of stocks and price               

        self.portfolio = {}

        ######################################################

        # Corretagem

        self.broker_fee = 0.

        ######################################################

        # Interest

        self.interest = 1.

        ######################################################

        # Leverage

        self.leverage = 1.  # 1. means NO LEVERAGE
        self.stop_operation = False

        ######################################################

        # Buy intention - dictionary
        # FORMAT ticker:(0 or 1) for buy or wait respectively

        self.buy_intention = {}

        ######################################################

        # Last operation order and buy intention

        self.last_order = {}
        
        self.buy_cause = {}
        self.sell_cause = {}

        ######################################################

        # Statistic measures variables

        self.sell_count = 0.
        self.gain_count = 0.
        self.buy_count = 0.

        self.total_cash_log = [self.total_initcash]
        self.cash_log = [self.cash]

        ######################################################

        # Working Days dictionary - BACKTEST ONLY?

        self.wd = working_days

        ######################################################

        # Stop win / Stop loss / operation_period

        self.stop_win = None
        self.stop_loss = None

        self.operation_period = dt.timedelta(0)

        # Operational varibles

        self.init_period_date = None  # dt.datetime
        self.end_period_date = None  # dt.datetime
        self.init_period_cash = None
        self.last_operational_date = dt.datetime.min

        ######################################################

        # DataBase

        self.database = database

        ######################################################

        # OptimalF return_dictionary simulation variable

        self.rd_of = {}
        self.flog_of = {}
    
    def get_strategy_struct(self):
        
        return self.strategy_variables,self.strategy

    @staticmethod
    def clear_facts(workmemory, ticker):

        # This function turns all Slave Facts to Invalid, consequently creating them on the WM if they do not exist.
        ######################################################

        workmemory[ticker]['DAY_COUNT'] = 'I'
        workmemory[ticker]['VOLUME'] = 'I'
        workmemory[ticker]['BOUGHT_PRICE'] = 'I'
        workmemory[ticker]['MY_CASH'] = 'I'

        return workmemory

        ######################################################

    def set_database(self,database):

        self.database = database

    def set_workingdays(self,wd):

        self.wd = wd

    def update_portfolio_intention(self, workmemory):

        ######################################################        

        for eachKey in workmemory.keys():

            if eachKey not in self.portfolio.keys():

                self.portfolio[eachKey] = []
                self.flog_of[eachKey] = []
                
                self.buy_cause[eachKey] = []
                self.sell_cause[eachKey] = []

                self.buy_intention[eachKey] = 0

                self.last_order[eachKey] = {"BUY": None, "SELL": []}

                initlog = {'DATE': 0, 'OPERATION': "START", 'VOLUME': 0, 'PRICE': 0, 'TOTAL_CASH': 0}
                self.operation_log[eachKey] = [initlog]

            else:

                pass

                ######################################################

    def set_risk_weights(self, dict_or_value):

        if type(dict_or_value) in (float, int):
            risk_list = {}
            for eachKey in self.portfolio.keys():
                risk_list[eachKey] = dict_or_value
            self.risk_weights = risk_list
        elif type(dict_or_value) == dict and dict_or_value != {}:
            self.risk_weights = dict_or_value
        else:
            raise Exception("Risk deve ser dictionary ou valor")

    def set_brokerfee(self, corr):

        self.broker_fee = corr

    def set_interest(self, year_interest):

        self.interest = year_interest ** (1. / 252)

    def set_leverage(self, lev):

        self.leverage = lev

    def set_stopwin(self, win):

        self.stop_win = win

    def set_stoploss(self, loss):

        self.stop_loss = loss

    def set_operation_period(self, timedelta):

        self.operation_period = timedelta

    def feed_workmemory(self, workmemory, ticker, stock_data, current_date):

        # This function feeds the workmemory with variables from the TRADER
        ######################################################

        # Into the WM
        if workmemory[ticker]['INVALID_DATE']:

            pass

        else:

            if stock_data != []:

                bought_price = stock_data['PRICE']
                volume = stock_data['VOLUME']
                date = stock_data['DATE']
                day_count = self.wd[ticker].index(current_date) - self.wd[ticker].index(date)

            else:

                bought_price = 0.
                day_count = 0.
                volume = 0.

            workmemory[ticker]['STOCK_VOLUME'] = volume
            workmemory[ticker]['DAY_COUNT'] = day_count
            workmemory[ticker]['BOUGHT_PRICE'] = bought_price
            workmemory[ticker]['TOTAL_CASH'] = self.total_cash(workmemory)
            workmemory[ticker]["LAST_OP"] = self.operation_log[ticker][-1]['OPERATION']
            
            r = random.random()
            workmemory[ticker]['RAND'] = r
            
        # Adicionar MAX_CASH_SO_FAR?

        return workmemory

        ######################################################

    def clear_portfolio_data(self, ticker):

        nonecount = self.portfolio[ticker].count(None)

        for i in range(nonecount):
            self.portfolio[ticker].remove(None)

    def clear_buy_intention(self):

        for eachKey in self.buy_intention.keys():
            self.buy_intention[eachKey] = 0

    def inference_engine(self, workmemory, ticker):

        ######################################################

        # Downwards inference engine

        workmemory[ticker]["BUY"] = False
        workmemory[ticker]["SELL"] = False
        self.buy_cause[ticker] = []
        
        buy_flag = False
        sell_flag = False

        if not workmemory[ticker]['INVALID_DATE']:

            for eachRule in self.strategy:
                workmemory[ticker],track = tradex.execrule(eachRule, workmemory[ticker],ret_track = True)
                
                if (buy_flag == False) and (workmemory[ticker]['BUY'] == True):
                    buy_flag = True
                    self.buy_cause[ticker] = [eachRule[0],track]
                    
                if (sell_flag == False) and (workmemory[ticker]['SELL'] == True):
                    sell_flag = True
                    self.sell_cause[ticker].append([eachRule[0],track])
        else:

            pass

        return workmemory

        ######################################################

    def make_operation_order(self, workmemory, ticker, stock_data):

        current_workmemory = workmemory[ticker]

        if current_workmemory['INVALID_DATE'] == False:

            if current_workmemory['SELL'] == True and stock_data != []:

                self.last_order[ticker]['SELL'].append(stock_data)

            elif current_workmemory['SELL'] == False and stock_data != []:  # Append for NON REALISED RETURN

                stock_data_index = self.portfolio[ticker].index(stock_data)

                self.portfolio[ticker][stock_data_index]['NRR'].append(current_workmemory['PRICE'])

            else:
                pass

            if current_workmemory['BUY']:

                self.buy_intention[ticker] = 1

            else:  # BUY = FALSE

                pass

        else:  # Invalid date pass

            pass

    def sell_all_order(self):

        for eachTicker in self.portfolio.keys():

            for eachStock in self.portfolio[eachTicker]:

                if eachStock is not None:
                    self.last_order[eachTicker]['SELL'].append(eachStock)

    def apply_risk_management(self, workmemory, risk_management, current_date):

        funstr = repr(risk_management).split(' ')[1]

        ############################################################################################################

        if funstr == repr(risklib.bet_all).split(' ')[1]:

            # Divisao igualitaria de capital por acao

            divisions = len(workmemory.keys())  # sum(self.buy_intention.values())

            if divisions != 0.:

                cash_per_stock = (self.cash * self.leverage) / divisions

                for ticker in self.buy_intention.keys():

                    current_workmemory = workmemory[ticker]

                    if self.buy_intention[ticker] == 1:

                        qtty = int(risk_management(cash_per_stock, current_workmemory['PRICE']) / 100.) * 100

                        if qtty <= current_workmemory['VOLUME']:

                            pass

                        else:

                            qtty = current_workmemory['VOLUME']

                        # print ticker, Quantity
                        if qtty != 0.:

                            self.last_order[ticker]['BUY'] = qtty

                        else:

                            pass

        ############################################################################################################

        if funstr == repr(risklib.fixed_per).split(' ')[1]:

            # Divisao igualitaria de capital por acao

            divisions = len(workmemory.keys())  # sum(self.buy_intention.values())

            if divisions != 0.:

                cash_per_stock = self.cash / divisions

                for ticker in self.buy_intention.keys():

                    current_workmemory = workmemory[ticker]

                    if self.buy_intention[ticker] == 1:

                        qtty = int(risk_management(cash_per_stock, 0.1, 0.05) / 100.0) * 100

                        if qtty <= current_workmemory['VOLUME']:

                            pass

                        else:

                            qtty = current_workmemory['VOLUME']

                        if (qtty * current_workmemory['PRICE']) > (cash_per_stock * self.leverage):

                            qtty = int(((cash_per_stock * self.leverage) / current_workmemory['PRICE']) / 100.) * 100


                        else:

                            pass

                            #                        print ticker, Quantity
                        self.last_order[ticker]['BUY'] = qtty

        ############################################################################################################

        if funstr == repr(risklib.fractioned).split(' ')[1]:

            for ticker in self.buy_intention.keys():

                current_workmemory = workmemory[ticker]

                if self.buy_intention[ticker] == 1:

                    qtty = int(
                        risk_management(current_workmemory, self.cash * self.leverage,
                                        self.risk_weights[ticker]) / 100.0) * 100

                    if qtty <= current_workmemory['VOLUME']:

                        pass

                    else:

                        qtty = current_workmemory['VOLUME']

                    self.last_order[ticker]['BUY'] = qtty

        ############################################################################################################

        if funstr == repr(risklib.optimalf).split(' ')[1]:

            intention = np.array(self.buy_intention.values())

            if sum(intention) != 0:

                if self.rd_of == {}:

                    dict_size = 20

                    sim_aq_init_date = current_date - dt.timedelta((10 * dict_size) + 30)
                    sim_init_date = current_date - dt.timedelta(10 * dict_size)

                    print "Simulating trader for optimal_f function"

                    sim_slave = backtest_simulation_acquisition(self.get_strategy_struct(), self.portfolio.keys(), self.cash,
                                                                (sim_aq_init_date, current_date),
                                                                (sim_init_date, current_date), risklib.bet_all,
                                                                brokerfee=self.broker_fee, leverage=self.leverage,
                                                                interest=self.interest,
                                                                show_statistics=False)
                    print 'Trader simulated.'
                    rd = sim_slave.return_dictionary(log_return=True, max_ret=dict_size)

                    self.rd_of = rd

                else:

                    self.rd_of = self.update_return_dictionaries(self.rd_of)

                f = risk_management(self.rd_of, self.leverage, [100, int(200 * self.leverage)])

                zero_count = 0
                for i in np.array(f) * intention:
                    if i == 0.:
                        zero_count += 1.

                divisions = len(workmemory.keys()) - zero_count

                if divisions == 0:
                    pass
                else:
                    cash_per_stock = self.cash / divisions

                    f_index = 0

                    for ticker in self.buy_intention.keys():

                        current_workmemory = workmemory[ticker]

                        if self.buy_intention[ticker] == 1:
                            
                            self.flog_of[ticker].append(f[f_index])

                            allocated_cash = cash_per_stock * f[f_index]

                            qtty = risklib.bet_all(allocated_cash, current_workmemory['PRICE'])
                            qtty = int(qtty / 100.) * 100

                            if qtty <= current_workmemory['VOLUME']:

                                pass

                            else:

                                qtty = current_workmemory['VOLUME']

                            self.last_order[ticker]['BUY'] = qtty

                        f_index += 1

    def perform_sell_order(self, workmemory, current_date):

        for eachStock in self.last_order.keys():

            current_workmemory = workmemory[eachStock]

            if self.last_order[eachStock]['SELL'] != []:

                inference = self.sell_cause[eachStock]

                sell_qtty = 0
                sell_return = 0.
                sell_logreturn = 0.
                sell_exposition_days = 0.
                
                for eachOrder in self.last_order[eachStock]['SELL']:
                    
                    stock_data_index = self.portfolio[eachStock].index(eachOrder)

                    sell_qtty += eachOrder['VOLUME']
                    sell_return += eachOrder['VOLUME'] * (current_workmemory['PRICE'] / eachOrder['PRICE'])
                    sell_logreturn += eachOrder['VOLUME'] * math.log(current_workmemory['PRICE'] / eachOrder['PRICE'])
                    sell_exposition_days += (self.wd[eachStock].index(current_date) - self.wd[eachStock].index(eachOrder['DATE']))
                    
                    self.portfolio[eachStock][stock_data_index] = None

                self.cash += current_workmemory['PRICE'] * sell_qtty
                self.cash -= self.broker_fee  # CORRETAGEM

                self.sell_count += 1

                sell_return = sell_return / sell_qtty
                sell_logreturn = sell_logreturn / sell_qtty

                log = {'DATE': current_date, 'OPERATION': "SOLD", 'VOLUME': sell_qtty,
                       'PRICE': current_workmemory['PRICE'],
                       'SPECIFICATION': self.last_order[eachStock]['SELL'], 'RETURN': sell_return,
                       'LOGRETURN': sell_logreturn,
                       'INFERENCE':inference,
                       'EXPOSITION':sell_exposition_days}

                self.operation_log[eachStock].append(log)

            self.last_order[eachStock]['SELL'] = []
            self.clear_portfolio_data(eachStock)

    def perform_buy_order(self, workmemory, current_date):

        for eachStock in self.last_order.keys():

            current_workmemory = workmemory[eachStock]

            if self.last_order[eachStock]['BUY'] not in (None, 0.):

                inference = self.buy_cause[eachStock]

                stock_information = {'DATE': current_date, 'VOLUME': self.last_order[eachStock]['BUY'],
                                     'PRICE': current_workmemory['PRICE'], 'NRR': []}

                self.cash -= (stock_information['VOLUME'] * stock_information['PRICE'])
                self.cash -= self.broker_fee  # CORRETAGEM

                self.buy_count += 1

                self.portfolio[eachStock].append(stock_information)

                log = {'DATE': current_date, 'OPERATION': "BOUGHT", 'VOLUME': stock_information['VOLUME'],
                       'PRICE': stock_information['PRICE'], 'SPECIFICATION': [],'INFERENCE':inference}
                self.operation_log[eachStock].append(log)

            self.last_order[eachStock]['BUY'] = None

    def perform_orders(self, workmemory, current_date, risk_management):

        ######################################################

        # Perform the whole buy/sell operation

        if self.init_period_date is None:

            self.init_period_date = current_date
            self.init_period_cash = self.total_cash(workmemory)
            self.end_period_date = self.init_period_date + self.operation_period

        else:

            if self.operation_period != dt.timedelta(0):

                if current_date > self.end_period_date:

                    self.init_period_date = current_date
                    self.init_period_cash = self.total_cash(workmemory)
                    self.end_period_date = self.init_period_date + self.operation_period

                    if self.stop_operation is True and (self.total_cash(workmemory) > 0):
                        self.stop_operation = False

        if not self.stop_operation:

            self.last_operational_date = current_date

            if self.cash < 0.:
                self.cash *= self.interest

            for eachStock in self.portfolio.keys():

                workmemory = self.clear_facts(workmemory, eachStock)
                stockData = self.portfolio[eachStock]
                self.sell_cause[eachStock] = []

                if stockData == []:  # Output -> Only BUY

                    workmemory = self.feed_workmemory(workmemory, eachStock, [], current_date)
                    workmemory = self.inference_engine(workmemory, eachStock)
                    self.make_operation_order(workmemory, eachStock, [])

                else:  # Output -> BUY AND SELL

                    for eachStockOp in stockData:
                        workmemory = self.feed_workmemory(workmemory, eachStock, eachStockOp, current_date)
                        workmemory = self.inference_engine(workmemory, eachStock)
                        self.make_operation_order(workmemory, eachStock, eachStockOp)

                        #            print "Dinheiro vivo antes de venda: ",self.cash

            self.perform_sell_order(workmemory, current_date)

            if self.total_cash(workmemory) <= 0.:
                self.stop_operation = True
                self.sell_all_order()
                self.perform_sell_order(workmemory, current_date)
                # vender tudo quando quebrar

            if self.cash > 0. and self.stop_operation == False:
                self.apply_risk_management(workmemory, risk_management, current_date)
                self.perform_buy_order(workmemory, current_date)

            if self.stop_win != None:
                if (self.total_cash(workmemory) / self.init_period_cash) >= self.stop_win:

                    self.stop_operation = True
                    self.sell_all_order()
                    self.perform_sell_order(workmemory, current_date)

            if self.stop_loss != None:
                if (self.total_cash(workmemory) / self.init_period_cash) <= self.stop_loss:

                    self.stop_operation = True
                    self.sell_all_order()
                    self.perform_sell_order(workmemory, current_date)

            # vende tudo ao atingir stop_win ou stop_loss no periodo

        else:
            pass

        self.clear_buy_intention()
        self.total_cash_log.append(self.total_cash(workmemory))
        self.cash_log.append(self.cash)

    def total_cash(self, workmemory):

        total_cash = self.cash

        for eachKey in self.portfolio.keys():

            for eachData in self.portfolio[eachKey]:
                total_cash += eachData['VOLUME'] * workmemory[eachKey]['PRICE']

        return total_cash

    def cash_in_portfolio(self, workmemory):

        cip = 0.

        for eachKey in self.portfolio.keys():

            for eachData in self.portfolio[eachKey]:
                cip += eachData['VOLUME'] * workmemory[eachKey]['PRICE']

        return cip

    def resumed_portfolio(self):

        resumedport = {}

        for eachKey in self.portfolio.keys():

            stock_volume = 0.

            for eachStockData in self.portfolio[eachKey]:
                stock_volume += eachStockData['VOLUME']

            resumedport[eachKey] = int(stock_volume)

        return resumedport

    def win_rate(self,briefedPortfolio = True):
        
        win_dict = {}
        totalSell = []

        
        if self.operation_log > 1:
            
            for eachStock in self.operation_log:
                
                logList = []
    
                for eachOp in range(len(self.operation_log[eachStock])):
                    
                    if 'LOGRETURN' not in self.operation_log[eachStock][eachOp]:
                        pass
                    
                    else:
                        logList.append(self.operation_log[eachStock][eachOp]['LOGRETURN'])
    
                logList = np.array(logList) +  1
    
                soldCount = float(len(logList))
                totalSell.append(soldCount)
                positive = copy.deepcopy(logList)
                
                if soldCount == 0: 
                    win_dict[eachStock] = 'no trade'
                else:
                    
                    
                    positive[positive > 1.] = 1.
        
                    
                    win   = list(positive).count(1.)/soldCount
        
                    
                    win_dict[eachStock] = win
                    
            if briefedPortfolio is True:
                
                mean = 0.
                count = 0.
                
                for value in win_dict.values():
                    
                    if value == 'no trade':
                        pass
                    else:
                        mean += value
                        count += 1.
                
                if count == 0.:
                    return 'no trade.'
                else:
                    return mean/count
    
            else:

                return win_dict
        
        else:
            
            return 0.

    def max_drowndown(self, in_cash=False):

        dd = []
        index_list = []

        for index in range(len(self.total_cash_log) - 1):
            value = self.total_cash_log[index]

            aheadmin = min(self.total_cash_log[index:])

            dd.append(value - aheadmin)
            index_list.append(index)

        ind = dd.index(max(dd))
        ind2 = index_list[ind]

        if not in_cash:
            return max(dd) / self.total_cash_log[ind2]
        else:
            return max(dd)

    def profit_factor(self, exp=False):  # LEVA O VOLUME EM CONTA TAMBEM?

        if self.sell_count == 0:
            print "No sells during the transaction period. 0 returned."
            return 0

        sumup = []
        sumdown = []

        for eachStock in self.portfolio.keys():

            for index in range(len(self.operation_log[eachStock])):

                myop = self.operation_log[eachStock][index]

                if myop['OPERATION'] == "SOLD":

                    up = 0.
                    down = 0.

                    for stock_data in myop['SPECIFICATION']:

                        if (myop['PRICE'] - stock_data['PRICE']) > 0.:

                            up += (myop['PRICE'] - stock_data['PRICE']) * stock_data['VOLUME']

                        elif (myop['PRICE'] - stock_data['PRICE']) < 0.:

                            down += abs(myop['PRICE'] - stock_data['PRICE']) * stock_data['VOLUME']

                    down += self.broker_fee

                    sumup.append(up)
                    sumdown.append(down)

        sumup = sum(sumup)
        sumdown = sum(sumdown)

        if not exp:
            return sumup / sumdown
        else:
            return math.exp(sumup) / math.exp(sumdown)

    def payoff(self):

        if self.sell_count == 0:
            print "No sells during the transaction period. 0 returned."
            return 0

        sumup = []
        sumdown = []

        for eachStock in self.portfolio.keys():

            for index in range(len(self.operation_log[eachStock])):

                myop = self.operation_log[eachStock][index]

                if myop['OPERATION'] == "SOLD":

                    up = 0.
                    down = 0.

                    for stock_data in myop['SPECIFICATION']:

                        if (myop['PRICE'] - stock_data['PRICE']) > 0.:

                            up += (myop['PRICE'] - stock_data['PRICE']) * stock_data['VOLUME']

                        elif (myop['PRICE'] - stock_data['PRICE']) < 0.:

                            down += abs(myop['PRICE'] - stock_data['PRICE']) * stock_data['VOLUME']

                    down += self.broker_fee

                    sumup.append(up)
                    sumdown.append(down)

        avgup = sum(sumup) / len(sumup)
        avgdown = sum(sumdown) / len(sumdown)

        return avgup / avgdown

    def calculate_gain_count(self):

        gc = 0.

        for eachStock in self.portfolio.keys():

            for index in range(len(self.operation_log[eachStock])):

                myop = self.operation_log[eachStock][index]

                if myop['OPERATION'] == "SOLD":

                    up = 0.
                    down = 0.

                    for stock_data in myop['SPECIFICATION']:

                        if (myop['PRICE'] - stock_data['PRICE']) > 0.:

                            up += ((myop['PRICE'] - stock_data['PRICE']) * stock_data['VOLUME'])

                        elif (myop['PRICE'] - stock_data['PRICE']) < 0.:

                            down += (abs(myop['PRICE'] - stock_data['PRICE']) * stock_data['VOLUME'])

                    if up > (down + self.broker_fee):  # DOWN + CORRETAGEM

                        gc += 1

        self.gain_count = gc
        return gc
    
    def vince(self,max_ret = 50):

        Stats = {}
        for eachStock in self.operation_log.keys():             
            trades      = []

            for eachOp in range(len(self.operation_log[eachStock])):
                    
                if 'LOGRETURN' not in self.operation_log[eachStock][eachOp]:
                    pass
                
                else:
                    trades.append(self.operation_log[eachStock][eachOp]['LOGRETURN'])
           
            trades  = np.array(trades)
            max_ret = len(trades)
            trades += 1

            if max_ret == 0.:
                
                Stats[eachStock] = {'AHPR': 0.,
                                'GATP': 0.,
                                'GATN': 0.,
                                'PayOff': 0.,
                                'SD': 0., 
                                'ETWR': 0.,
                                'TWR': 0.}
                return Stats
            else:
            
                positive,negative = copy.deepcopy(trades),copy.deepcopy(trades)
    
                positive[positive > 1.] = 1.
                negative[negative < 1.] = 1.
                
                win  = list(positive).count(1.)
                loss = list(negative).count(1.)
                
                if win == max_ret:
                    GATPositive = 0.
                else:
                    GATPositive = np.prod(negative)**(1./(max_ret-loss))
                if loss == max_ret:
                    GATNegative = 0.
                else:
                    GATNegative = np.prod(positive)**(1./(max_ret-win))
                print win,loss,GATPositive,GATNegative
                if GATPositive and GATNegative == 0:
                    PayOff = 0.
                else:
                    PayOff = GATPositive/GATNegative
                
                Stats[eachStock] = {'AHPR': np.mean(trades[-max_ret:]),
                                    'GATP': GATPositive,
                                    'GATN': GATNegative,
                                    'PayOff': PayOff,
                                    'SD': np.std(trades[-max_ret:]), 
                                    'ETWR': (np.mean(trades[-max_ret:])**2 - np.std(trades[-max_ret:])**2)**(1./len(trades[-max_ret:])),
                                    'TWR': np.prod(trades[-max_ret:]) }
            
            return Stats

    def expected_value(self,briefedPortfolio = True):
        ME = {}
        if self.sell_count == 0:

            print " No sells during the transaction period. 0 returned"

            return 0.

        else:

            weight    = np.array([np.exp(-i) for i in np.arange(0.5,1.,0.5/len(self.operation_log.keys()))])
            boxes     = np.round(np.arange(10,50,40./len(self.operation_log.keys())))
            
            for eachStock in self.operation_log.keys():
             
                trades      = []
                partialME   = []
                
                for eachOp in range(len(self.operation_log[eachStock])):
                    
                    if 'LOGRETURN' not in self.operation_log[eachStock][eachOp]:
                        pass
                    
                    else:
                        trades.append(self.operation_log[eachStock][eachOp]['LOGRETURN'])

                trades   = np.array(trades) +  1
                positive,negative = copy.deepcopy(trades),copy.deepcopy(trades)

                positive[positive > 1.] = 1.
                negative[negative < 1.] = 1.

                stopFlag = len(trades) > boxes

                if False in stopFlag:
                    tradeBox = boxes[list(stopFlag).index(False):]

                elif stopFlag[0] is False:
                    tradeBox = len(trades)                    
                
                else:
                    tradeBox = boxes
                    
                tradeBox = list(tradeBox) 
                for boxSize in tradeBox:
                    
                    self.upTrades, self.downTrades = copy.deepcopy(trades[-boxSize:]),copy.deepcopy(trades[-boxSize:])
                    
                    self.upTrades[self.upTrades < 1.] = 1.
                    self.expPositive = list(self.upTrades).count(1.)

                    self.downTrades[self.downTrades > 1.] = 1.
                    self.expNegative = list(self.downTrades).count(1.)

                    if self.expPositive - len(self.upTrades) == 0. :
                        self.GATPositive = 0.
                    else:
                        self.GATPositive = np.prod(self.upTrades)**(1./(len(self.upTrades) - self.expPositive))

                    if self.expNegative - len(self.downTrades) == 0.:
                        self.GATNegative = 0.
                    else:                                
                        self.GATNegative = np.prod(self.downTrades)**(1./(len(self.downTrades)- self.expNegative))
                        
                    
                    win              = boxSize - self.expPositive
                    loss             = boxSize - self.expNegative
                    
                    partialME.append(self.GATPositive*(win/float(boxSize)) - self.GATNegative*((loss/float(boxSize))))
                    
                    
                partialME       = np.array(partialME)
                if len(partialME) > 1:
                    weightedAverage = np.average(partialME)
                else:
                    weightedAverage = partialME
                ME[eachStock]   = weightedAverage
                
        if briefedPortfolio is not True:
                
            return ME 
        else:
            return np.prod(ME.values())
            
    def recovery_factor(self):

        gain = (self.total_cash_log[-1] - self.total_initcash)

        if self.max_drowndown(in_cash=True) == 0.:
            return gain
        else:
            return gain / self.max_drowndown(in_cash=True)

    def max_min(self):

        return max(self.total_cash_log), min(self.total_cash_log)

    def return_dictionary(self, log_return=False, ret_inv=False, max_ret=50, stock_filter=[], from_date_dict=None):

        returns = {}
        invs = {}

        if stock_filter != []:

            stock_list = stock_filter

        else:

            stock_list = self.portfolio.keys()

        for eachKey in stock_list:

            stockreturn = [0 for i in range(max_ret)]
            stockinvest = [0 for i in range(max_ret)]
            dates = [dt.datetime(1677, 9, 23, 0, 0) for i in range(max_ret)]

            index = max_ret

            operations = copy.deepcopy(self.operation_log[eachKey])
            operations.reverse()

            for eachOp in operations:

                if type(from_date_dict) == dict and type(eachOp['DATE']) == dt.datetime:

                    from_date = from_date_dict[eachKey]

                    if eachOp['DATE'] > from_date:
                        if eachOp['OPERATION'] == 'SOLD':

                            index -= 1

                            if log_return:
                                stockreturn[index] = eachOp['LOGRETURN']
                            else:
                                stockreturn[index] = eachOp['RETURN']

                            stockinvest[index] = (eachOp['PRICE'] * eachOp['VOLUME']) / eachOp['RETURN']
                            dates[index] = eachOp['DATE']

                        if index == 0:
                            break
                        else:
                            pass

                else:

                    if eachOp['OPERATION'] == 'SOLD':

                        index -= 1

                        if log_return:
                            stockreturn[index] = eachOp['LOGRETURN']
                        else:
                            stockreturn[index] = eachOp['RETURN']

                        stockinvest[index] = (eachOp['PRICE'] * eachOp['VOLUME']) / eachOp['RETURN']
                        dates[index] = eachOp['DATE']

                    if index == 0:
                        break
                    else:
                        pass

            if type(from_date_dict) == dict:
                stockreturn = stockreturn[index:]
                stockinvest = stockinvest[index:]
                dates = dates[index:]

            returns[eachKey] = pandas.Series(stockreturn, index=dates)
            invs[eachKey] = pandas.Series(stockinvest, index=dates)

        if ret_inv:

            return returns, invs

        else:

            return returns

    def update_return_dictionaries(self, old_d, log_return=True):

        updated_dict = copy.deepcopy(old_d)
        max_datetimes = {}

        for eachkey in old_d.keys():
            max_datetimes[eachkey] = max(old_d[eachkey].index)

        new_d = self.return_dictionary(log_return=log_return, from_date_dict=max_datetimes)

        for eachkey in new_d.keys():

            if eachkey in old_d.keys():
                old_series = old_d[eachkey]
                new_series = new_d[eachkey]

                size = len(old_series)

                updated_series = pandas.concat([old_series, new_series])

                index = len(updated_series) - size

                updated_series = updated_series[index:]

                updated_dict[eachkey] = updated_series

        return updated_dict


########################################################################################################################################################################################################################

def backtest_simulation_acquisition(strategy_or_location, stocks, cash, acquisition_range, operation_range,
                                    risk_function,
                                    source='bitfinex',
                                    brokerfee=14.9,
                                    leverage=1.,
                                    interest=1.19,
                                    stop_win=None,
                                    stop_loss=None,
                                    operation_period=0,
                                    show_statistics=True,
                                    show_dates=False):
    import data_handler
    import datetime as dt
    import tradex
    import matplotlib.pyplot as plt

    if type(acquisition_range[0]) == dt.datetime:
        start_aq = acquisition_range[0]
    else:
        start_aq = dt.datetime(*acquisition_range[0])

    if type(acquisition_range[1]) == dt.datetime:
        end_aq = acquisition_range[1]
    else:
        end_aq = dt.datetime(*acquisition_range[1])

    if type(operation_range[0]) == dt.datetime:
        start_op = operation_range[0]
    else:
        start_op = dt.datetime(*operation_range[0])

    if type(operation_range[1]) == dt.datetime:
        end_op = operation_range[1]
    else:
        end_op = dt.datetime(*operation_range[1])

    ############################################################################################################
    if type(strategy_or_location) == str:
        strategy_struct = tradex.read_kb(strategy_or_location)
    else:
        strategy_struct = strategy_or_location
    
    ############################################################################################################

    ############################################################################################################

    print type(start_aq), start_aq, type(end_aq), end_aq

    database = data_handler.database_builder(stocks, start_aq, end_aq, source=source)
    indicators, working_days = data_handler.calculate_indicators(stocks, database,indicator_filter = strategy_struct[0])
    print 'Indicators calculated.'
    workmemory = data_handler.workmemory_builder(stocks)
    ############################################################################################################

    # Gera entidade SlaveTrader para operar

    trader = SlaveTrader(strategy_struct, working_days, initcash=cash, database=indicators)
    trader.update_portfolio_intention(workmemory)
    trader.set_brokerfee(brokerfee)
    trader.set_leverage(leverage)
    trader.set_interest(interest)
    trader.set_stoploss(stop_loss)
    trader.set_stopwin(stop_win)
    trader.set_operation_period(dt.timedelta(operation_period))

    ############################################################################################################

    stop_flag = False
    day_list = [start_op]

    while not stop_flag:
        next_day = day_list[-1] + dt.timedelta(days=1)
        day_list.append(next_day)

        if next_day >= end_op:
            stop_flag = True
        else:
            pass

    ############################################################################################################
    print 'Simulating ... please wait.'
    for current_date in day_list:
        ############################################################################################################
        if show_dates:
            print 'Simulating date: ', current_date
        workmemory = data_handler.workmemory_feeder(workmemory, trader, current_date,indicator_filter = strategy_struct[0])  # Updates WM

        ############################################################################################################

        trader.perform_orders(workmemory, current_date, risk_function)  # Slave Perform operations

        ############################################################################################################

    if show_statistics:

        print '=' * 50
        print ''
        print "Inicio de operacao em: ", start_op
        print ''
        print "Cash inicial: ", cash
        print "Situacao final: ", trader.resumed_portfolio()

        print ''

        print "Dinheiro em caixa", trader.cash
        print "Dinheiro em portfolio atual", trader.cash_in_portfolio(workmemory)
        print ''
        print "Dinheiro total: ", trader.total_cash(workmemory)
        print "Profit total no periodo (%):", trader.total_cash(workmemory) / cash
        print ''
        print "Fim de operacao em: ", current_date

        print ""
        print "Medidas estatisticas: "
        print "Taxa de acerto: ", trader.win_rate(briefedPortfolio = True)
        print "Expectativa Matematica: ", trader.expected_value()
        print "Recovery Factor: ", trader.recovery_factor()
        print "Max DD: ", trader.max_drowndown()
        print "Profit Factor: ", trader.profit_factor()
        print "PayOff: ", trader.payoff()
        print "Max Min: ", trader.max_min()

        plt.interactive(False)
        plt.figure()
        plt.plot(range(len(trader.total_cash_log)),trader.total_cash_log, 'b',range(len(trader.total_cash_log)),trader.total_cash_log,'k')
        plt.title(strategy_or_location + ' total cash.')
        plt.xlabel('Dias uteis')
        plt.ylabel('Unidade monetaria')
        plt.show()

        plt.figure()
        plt.plot(trader.total_cash_log, 'b')
        plt.title('total cash & cash log')
        plt.plot(trader.cash_log, 'k')

        plt.xlabel('Dias uteis')
        plt.ylabel('Unidade monetaria')
        # plt.show()

    else:
        pass

    return trader


########################################################################################################################################################################################################################

########################################################################################################################################################################################################################

def BacktestLoader(strategy_location, stocks, cash, database_or_location, operation_range, risk_function,
                   brokerfee=14.9,
                   leverage=1.,
                   interest=1.19):
    import data_handler
    import tradex
    import matplotlib.pyplot as plt

    start_op = dt.datetime(*operation_range[0])
    end_op = dt.datetime(*operation_range[1])

    ############################################################################################################
    if type(database_or_location) == str:
        database = data_handler.database_loader(database_or_location)
    else:
        database = database_or_location

    indicators, working_days = data_handler.calculate_indicators(stocks, database)
    print 'Indicators calculated.'

    workmemory = data_handler.workmemory_builder(stocks)
    ############################################################################################################

    ############################################################################################################
    current_strategy = tradex.read_kb(strategy_location)
    ############################################################################################################

    # Gera entidade SlaveTrader para operar

    trader = SlaveTrader(current_strategy, working_days, initcash=cash, database=indicators)
    trader.update_portfolio_intention(workmemory)
    trader.set_brokerfee(brokerfee)
    trader.set_leverage(leverage)
    trader.set_interest(interest)

    ############################################################################################################

    stop_flag = False
    day_list = [start_op]

    while stop_flag == False:
        next_day = day_list[-1] + dt.timedelta(days=1)
        day_list.append(next_day)

        if next_day >= end_op:
            stop_flag = True
        else:
            pass

    ############################################################################################################
    print 'Simulating ... please wait.'
    for current_date in day_list:
        ############################################################################################################

        workmemory = data_handler.workmemory_feeder(workmemory, trader, current_date)  # Updates WM

        ############################################################################################################

        trader.perform_orders(workmemory, current_date, risk_function)  # Slave Perform operations

        ############################################################################################################

    print '=' * 50
    print ''
    print "Inicio de operacao em: ", start_op
    print ''
    print "Cash inicial: ", cash
    print "Situacao final: ", trader.resumed_portfolio()

    print ''

    print "Dinheiro em caixa", trader.cash
    print "Dinheiro em portfolio atual", trader.cash_in_portfolio(workmemory)
    print ''
    print "Dinheiro total: ", trader.total_cash(workmemory)
    print "Profit total no periodo (%):", trader.total_cash(workmemory) / cash
    print ''
    print "Fim de operacao em: ", current_date

    print ""
    print "Medidas estatisticas: "
    print "Taxa de acerto: ", trader.win_rate(brifedPortfolio = True)
    print "Expectativa Matematica: ", trader.expected_value()
    print "Recovery Factor: ", trader.recovery_factor()
    print "Max DD: ", trader.max_drowndown()
    print "Profit Factor: ", trader.profit_factor()
    print "PayOff: ", trader.payoff()
    print "Max Min: ", trader.max_min()

    plt.figure()
    plt.plot(trader.total_cash_log, 'b')
    plt.title(strategy_location + ' total cash.')
    plt.xlabel('Dias uteis')
    plt.ylabel('Unidade monetaria')
    plt.show()

    plt.figure()
    plt.plot(trader.total_cash_log, 'b')
    plt.title(strategy_location + ' total cash/cash')
    plt.plot(trader.cash_log, 'k')

    plt.xlabel('Dias uteis')
    plt.ylabel('Unidade monetaria')
    # plt.show()

    return trader

    ########################################################################################################################################################################################################################
