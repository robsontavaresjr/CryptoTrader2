# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 08:33:39 2016

@author: Aluno - Joao
"""
import robotlib as robot
import risklib
import matplotlib.pyplot as plt
import numpy as np

######################################################

# Aquisicao dos dados para CALCULO DE VARIAVEIS, nessa entidade start e end date devem ser o TIME_RANGE DE AQUISICAO DE DADOS. Ex: 5 anos atras
StrategyLocation = 'Strategies/giant_penis.txt'

# ==============================================================================
# USE SOMENTE SE A VARIÁVEL ToExcel NÃO ESTIVER MARCADA COMO TRUE
stocks = ['RADL3', 'CIEL3', 'CTIP3', 'BVMF3']#'PETR4','DASA3','NATU3','ITSA4']  # ,'NFLX','GOOG','FB','AMZN','AAPL']
# ==============================================================================
cash = 100E3

# DB = DataBaseLoader('Bovespa_2010_2016.pkl')

start_aq = (2014, 1, 1)
end_aq = (2016, 4, 10)
AqRange = [start_aq, end_aq]

start_op = (2015, 1, 1)
end_op = (2016, 4, 10)
OpRange = [start_op, end_op]

# ==============================================================================
Slave = robot.backtest_simulation_acquisition(StrategyLocation, stocks, cash, AqRange, OpRange,
                                              risklib.optimalf ,
                                              brokerfee=14.9,
                                              leverage=1.,
                                              interest=1.1913,
                                              stop_win=None,
                                              stop_loss=None,
                                              operation_period=0,
                                              plot_cashflow=True)
# ==============================================================================
