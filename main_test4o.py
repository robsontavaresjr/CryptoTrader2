# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 08:33:39 2016

@author: Aluno - Joao
"""

import risklib
import robotlib as robot

# Aquisicao dos dados para CALCULO DE VARIAVEIS, nessa entidade start e end date devem ser o TIME_RANGE DE AQUISICAO DE DADOS. Ex: 5 anos atras
StrategyLocation = 'Strategies/giant_penis.txt'

ticker = ['LTCUSD', 'BTCUSD']
source = "bitfinex"

cash = 1E9

start_aq = (2017, 1, 4)
end_aq = (2018, 4, 14)
AqRange = [start_aq, end_aq]

start_op = (2018,3, 1)
end_op = (2018, 4, 14)
OpRange = [start_op, end_op]

Slave = robot.backtest_simulation_acquisition(StrategyLocation, ticker, cash, AqRange, OpRange,
                                              risklib.bet_all,
                                              brokerfee=14.9,
                                              leverage=1.,
                                              interest=1.0615,
                                              stop_win=None,
                                              stop_loss=None,
                                              operation_period=0,
                                              show_statistics=True)