# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 08:33:39 2016

@author: Aluno - Joao
"""

import risklib
import matplotlib.pyplot as plt
import numpy             as np
import robotlib          as robot
from TA_Finder           import *
from TA_Trend            import *
######################################################

# Aquisicao dos dados para CALCULO DE VARIAVEIS, nessa entidade start e end date devem ser o TIME_RANGE DE AQUISICAO DE DADOS. Ex: 5 anos atras
StrategyLocation = 'Strategies/buy_n_hold.txt'

# ==============================================================================
# USE SOMENTE SE A VARIÁVEL ToExcel NÃO ESTIVER MARCADA COMO TRUE
stocks = ['BTCUSD']#'PETR4','DASA3','NATU3','ITSA4']  # ,'NFLX','GOOG','FB','AMZN','AAPL']
# ==============================================================================
cash = 100E3

# DB = DataBaseLoader('Bovespa_2010_2016.pkl')

start_aq = (2017, 1, 4)
end_aq   = (2018, 3, 2)
AqRange  = [start_aq, end_aq]

start_op = (2018,1, 3)
end_op = (2018, 3, 2)
OpRange = [start_op, end_op]


# ==============================================================================
Slave = robot.backtest_simulation_acquisition(StrategyLocation, stocks, cash, AqRange, OpRange,
                                              risklib.bet_all ,
                                              brokerfee=14.9,
                                              leverage=1.,
                                              interest=1.0615,
                                              stop_win=None,
                                              stop_loss=None,
                                              operation_period=0,
                                              show_statistics=True)
#==============================================================================
# # # ==============================================================================
# #
# # random = robot.backtest_simulation_acquisition(r'Strategies/atr_furious.txt', stocks, cash, AqRange, OpRange,
# #                                               risklib.bet_all ,
# #                                               brokerfee=14.9,
# #                                               leverage=1.,
# #                                               interest=1.1913,
# #                                               stop_win=None,
# #                                               stop_loss=None,
# #                                               operation_period=0,
# #                                               show_statistics=True)
# #
# # print " Average Ratio: ", np.mean(np.array(Slave.total_cash_log)/np.array(random.total_cash_log))
# #==============================================================================
# ind = Indicators(Slave)
# ta  = taAnalyst(ind,Slave,timeFrame = 9)
#
# for i in range(len(ta.keys())):
#     print ta.keys()[i], ta[ta.keys()[i]]
