# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 08:33:39 2016

@author: Aluno - Joao
"""
import robotlib as robot
import risklib
import matplotlib.pyplot as plt
import numpy as np
import xlwings as xl

######################################################
StrategyLocation = 'Strategies/giant_penis.txt'

indice = {'Liquidas': [[u'SUZB5'],[u'UGPA3'],[u'VALE3'],[u'WEGE3'],[u'TBLE3'],[u'PETR3'],[u'IGTA3'],[u'TRPL4'],[u'TOTS3'],[u'VLID3'],[u'TUPY3'],[u'TCSA3'],[u'TGMA3'],[u'TEMP3'],[u'CVCB3'],[u'LAME4'],[u'RADL3'],[u'CPLE6'],[u'RAPT4'],[u'ELPL4'],[u'BRAP4'],[u'BTOW3'],[u'CSNA3'],[u'EQTL3'],[u'QUAL3'],[u'CIEL3'],[u'ARZZ3'],[u'USIM5'],[u'RENT3'],[u'HGTX3'],[u'HYPE3'],[u'BBAS3'],[u'MYPK3'],[u'SBSP3'],[u'LREN3'],[u'ESTC3'],[u'BBDC4'],[u'BRFS3'],[u'CTIP3'],[u'VALE5'],[u'PCAR4'],[u'BRKM5'],[u'ITUB4'],[u'SMTO3'],[u'BRML3'],[u'CSAN3'],[u'ANIM3'],[u'MDIA3'],[u'VIVT4'],[u'FLRY3'],[u'JBSS3'],[u'EMBR3'],[u'CPFE3'],[u'ALSC3'],[u'BBDC3'],[u'AMAR3'],[u'FIBR3'],[u'MPLU3'],[u'ALPA4'],[u'ITUB3'],[u'PETR4'],[u'BEEF3'],[u'EZTC3'],[u'LINX3'],[u'CSMG3'],[u'ITSA4'],[u'SMLE3'],[u'CMIG4'],[u'BBSE3'],[u'ABCB4'],[u'CYRE3'],[u'NATU3'],[u'CESP6'],[u'CCRO3'],[u'SLCE3'],[u'BVMF3'],[u'TIMP3'],[u'LIGT3'],[u'PSSA3'],[u'MGLU3'],[u'GRND3'],[u'SEER3'],[u'OIBR3'],[u'MRFG3'],[u'LEVE3'],[u'DTEX3'],[u'KROT3'],[u'ABEV3'],[u'ODPV3'],[u'GOAU4'],[u'MILS3'],[u'GGBR4'],[u'EVEN3'],[u'MRVE3'],[u'LLIS3'],[u'PARC3'],[u'QGEP3'],[u'GFSA3'],[u'ENBR3'],[u'DIRR3'],[u'RUMO3'],[u'ECOR3'],[u'BRPR3'],[u'RLOG3'],[u'JHSF3'],[u'OIBR4'],[u'LPSB3']],
             'IBrA'     : [[u'ABCB4'],[u'ABEV3'],[u'ALPA4'],[u'ALSC3'],[u'ALUP11'],[u'ANIM3'],[u'ARTR3'],[u'BBAS3'],[u'BBDC3'],[u'BBDC4'],[u'BBSE3'],[u'BEEF3'],[u'BRAP4'],[u'BRFS3'],[u'BRIN3'],[u'BRKM5'],[u'BRML3'],[u'BRPR3'],[u'BRSR6'],[u'BTOW3'],[u'BVMF3'],[u'CCRO3'],[u'CESP6'],[u'CIEL3'],[u'CMIG4'],[u'CPFE3'],[u'CPLE6'],[u'CSAN3'],[u'CSMG3'],[u'CSNA3'],[u'CTIP3'],[u'CVCB3'],[u'CYRE3'],[u'DIRR3'],[u'DTEX3'],[u'ECOR3'],[u'ELET3'],[u'ELET6'],[u'ELPL4'],[u'EMBR3'],[u'ENBR3'],[u'EQTL3'],[u'ESTC3'],[u'EVEN3'],[u'EZTC3'],[u'FIBR3'],[u'FLRY3'],[u'GFSA3'],[u'GGBR4'],[u'GOAU4'],[u'GOLL4'],[u'GRND3'],[u'HBOR3'],[u'HGTX3'],[u'HYPE3'],[u'IGTA3'],[u'ITSA4'],[u'ITUB3'],[u'ITUB4'],[u'JBSS3'],[u'KLBN11'],[u'KROT3'],[u'LAME3'],[u'LAME4'],[u'LEVE3'],[u'LIGT3'],[u'LINX3'],[u'LREN3'],[u'MDIA3'],[u'MGLU3'],[u'MILS3'],[u'MPLU3'],[u'MRFG3'],[u'MRVE3'],[u'MULT3'],[u'MYPK3'],[u'NATU3'],[u'ODPV3'],[u'OIBR3'],[u'OIBR4'],[u'PARC3'],[u'PCAR4'],[u'PDGR3'],[u'PETR3'],[u'PETR4'],[u'POMO4'],[u'PRML3'],[u'PSSA3'],[u'QGEP3'],[u'QUAL3'],[u'RADL3'],[u'RAPT4'],[u'RENT3'],[u'RLOG3'],[u'RUMO3'],[u'SANB11'],[u'SBSP3'],[u'SEER3'],[u'SLCE3'],[u'SMLE3'],[u'SMTO3'],[u'SULA11'],[u'SUZB5'],[u'TAEE11'],[u'TBLE3'],[u'TCSA3'],[u'TIET11'],[u'TIMP3'],[u'TOTS3'],[u'TRPL4'],[u'TUPY3'],[u'UGPA3'],[u'USIM5'],[u'VALE3'],[u'VALE5'],[u'VIVT4'],[u'VLID3'],[u'VVAR11'],[u'WEGE3']], 
             'IBrX50'   : [[u'ABEV3'],[u'BBAS3'],[u'BBDC3'],[u'BBDC4'],[u'BBSE3'],[u'BRAP4'],[u'BRFS3'],[u'BRKM5'],[u'BRML3'],[u'BVMF3'],[u'CCRO3'],[u'CIEL3'],[u'CMIG4'],[u'CPFE3'],[u'CSAN3'],[u'CSNA3'],[u'CTIP3'],[u'CYRE3'],[u'EMBR3'],[u'EQTL3'],[u'ESTC3'],[u'FIBR3'],[u'GGBR4'],[u'GOAU4'],[u'HYPE3'],[u'ITSA4'],[u'ITUB4'],[u'JBSS3'],[u'KLBN11'],[u'KROT3'],[u'LAME4'],[u'LREN3'],[u'MRVE3'],[u'MULT3'],[u'NATU3'],[u'PCAR4'],[u'PETR3'],[u'PETR4'],[u'QUAL3'],[u'RADL3'],[u'RENT3'],[u'SMLE3'],[u'SUZB5'],[u'TIMP3'],[u'UGPA3'],[u'USIM5'],[u'VALE3'],[u'VALE5'],[u'VIVT4'],[u'WEGE3']]}
             
cash = 100E3

# DB = DataBaseLoader('Bovespa_2010_2016.pkl')

start_aq = (2014, 1, 1)
end_aq = (2016, 4, 27)
AqRange = [start_aq, end_aq]

start_op = (2015, 1, 1)
end_op = (2016, 4, 27)
OpRange = [start_op, end_op]
eachStock = 0
xl.Workbook()
for stocks in indice['IBrX50']:
         
    # ==============================================================================
    trader = robot.backtest_simulation_acquisition(StrategyLocation, stocks, cash,                                                AqRange,OpRange,
                                              risklib.bet_all ,
                                              brokerfee=14.9,
                                              leverage=1.,
                                              interest=1.1913,
                                              stop_win=None,
                                              stop_loss=None,
                                              operation_period=0,
                                              show_statistics=True)
    # ==============================================================================
                                              
    ## ==============================================================================
    
    header               = ['Stock','Win Rate','PayOff','AHPR','Std','MathExp','Profit Factor','Recovery Factor','Min @ Period','Max @ Period','Drawdown (%)','Drawdown ($)','Bid','Ask','Profit (%)','Profit ($)']
    
    strategy = StrategyLocation.replace("'\'","' '")
    
    xl.Range(1,(1,1)).value = strategy
    xl.Range(1,(2,1)).value = header
    
    xl.Range(1,(1,1)).offset(eachStock+2,0).value          = stocks[0]
        
    xl.Range(1,(1,2)).offset(eachStock+2,0).value          = trader.win_rate()
    xl.Range(1,(1,2)).offset(eachStock+2,0).number_format  = '#.##0,00;- #.##0,00'        
    
    xl.Range(1,(1,3)).offset(eachStock+2,0).value          = trader.vince()[trader.vince().keys()[0]]['PayOff']
    xl.Range(1,(1,3)).offset(eachStock+2,0).number_format  = '#.##0,00;- #.##0,00'
    
    xl.Range(1,(1,4)).offset(eachStock+2,0).value          = trader.vince()[trader.vince().keys()[0]]['AHPR']
    xl.Range(1,(1,4)).offset(eachStock+2,0).number_format  = '#.##0,00;- #.##0,00'

    xl.Range(1,(1,5)).offset(eachStock+2,0).value          = trader.vince()[trader.vince().keys()[0]]['SD']
    xl.Range(1,(1,5)).offset(eachStock+2,0).number_format  = '#.##0,00;- #.##0,00'


    xl.Range(1,(1,6)).offset(eachStock+2,0).value          = trader.expected_value()
    xl.Range(1,(1,6)).offset(eachStock+2,0).number_format  = '#.##0,00;- #.##0,00'
    
    xl.Range(1,(1,7)).offset(eachStock+2,0).value          = trader.profit_factor()
    xl.Range(1,(1,7)).offset(eachStock+2,0).number_format  = '#.##0,00;- #.##0,00'
    
    xl.Range(1,(1,8)).offset(eachStock+2,0).value          = trader.recovery_factor()                          
    xl.Range(1,(1,8)).offset(eachStock+2,0).number_format  = '#.##0,00;- #.##0,00'
    
    xl.Range(1,(1,9)).offset(eachStock+2,0).value          = trader.max_min()[-1]
    xl.Range(1,(1,9)).offset(eachStock+2,0).number_format  = 'R$ #.##0,00;-R$ #.##0,00'

    xl.Range(1,(1,10)).offset(eachStock+2,0).value          = trader.max_min()[0]
    xl.Range(1,(1,10)).offset(eachStock+2,0).number_format  = 'R$ #.##0,00;-R$ #.##0,00'

    xl.Range(1,(1,11)).offset(eachStock+2,0).value          = (trader.max_min()[0] - trader.max_min()[-1])/trader.max_min()[0]
    xl.Range(1,(1,11)).offset(eachStock+2,0).number_format  = '#.##0,00 %;- #.##0,00 %'                
    
    xl.Range(1,(1,12)).offset(eachStock+2,0).value         = trader.max_min()[0] - trader.max_min()[-1]
    xl.Range(1,(1,12)).offset(eachStock+2,0).number_format = 'R$ #.##0,00;-R$ #.##0,00'        
    
    xl.Range(1,(1,13)).offset(eachStock+2,0).value         = trader.buy_count
    xl.Range(1,(1,14)).offset(eachStock+2,0).value         = trader.sell_count

    xl.Range(1,(1,15)).offset(eachStock+2,0).value         = trader.total_cash_log[-1]/cash - 1
    xl.Range(1,(1,15)).offset(eachStock+2,0).number_format = '#.##0,00 %;- #.##0,00 %'        

    xl.Range(1,(1,16)).offset(eachStock+2,0).value         = trader.total_cash_log[-1] - cash        
    xl.Range(1,(1,16)).offset(eachStock+2,0).number_format = 'R$ #.##0,00;-R$ #.##0,00'        
    
    xl.Sheet(1).autofit()    

    eachStock += 1