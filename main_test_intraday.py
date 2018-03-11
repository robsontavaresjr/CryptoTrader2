# coding=utf-8
# import TA_Finder
# import TA_Trend
import risklib
import matplotlib.pyplot as plt
import numpy             as np
import robotlib_ID as robot
# import SlaveAnalyst      as SA

######################################################

# Aquisicao dos dados para CALCULO DE VARIAVEIS, nessa entidade start e end date devem ser o TIME_RANGE DE AQUISICAO DE DADOS. Ex: 5 anos atras
StrategyLocation = 'Strategies/buy_n_hold.txt'

# ==============================================================================
stocks =['NFLX','GOOG','FB','AMZN','AAPL'] # ['BVMF3','PETR4','DASA3','NATU3','ITSA4']  # ,
# ==============================================================================
cash = 100E3

interval = 300
daysBack = 10



Slave =  robot.backtest_simulation_acquisition(StrategyLocation, stocks, cash, interval, daysBack,
                                               risklib.bet_all,
                                               brokerfee=14.9,
                                               leverage=1.,
                                               interest=1.19,
                                               stop_win=None,
                                               stop_loss=None,
                                               plot_cashflow=True)

