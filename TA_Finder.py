# -*- coding: utf-8 -*-
"""
Created on Thu May 05 10:32:42 2016

@author: Suporte
"""

import numpy as np
import pandas as pd

def Indicators(Slave,position = 0):
    
    Indicator = {}        
    
    for eachStock in Slave.database.keys():
        
        ticker = Slave.database[eachStock]
   
    #==============================================================================
    #                   Dados técnicos
    #==============================================================================

        close = ticker['CLOSE']
        open_ = ticker['OPEN']
        high  = ticker['HIGH']
        low   = ticker['LOW']
        
        date  = ticker['CLOSE'].index
        
    #==============================================================================
    #              Japaneses Candle Sticks Identification
    #==============================================================================

        piercingDT,piercingDTDate = [],[]
        bullishEDT,bullishEDTDate = [],[]
        bullishHDT,bullishHDTDate = [],[]
        dccUT,dccUTDate           = [],[]
        bearishEUT,bearishEUTDate = [],[]
        bearishHUT,bearishHUTDate = [],[]
        
        bearish1,bearish1Date = [],[]
        bearish2,bearish2Date = [],[]
        bearish3,bearish3Date = [],[]
        bearish4,bearish4Date = [],[]
        bearish5,bearish5Date = [],[]
        
        bullish1,bullish1Date = [],[]
        bullish2,bullish2Date = [],[]
        bullish3,bullish3Date = [],[]
        bullish4,bullish4Date = [],[]
        bullish5,bullish5Date = [],[]
        
#==============================================================================
#       Identificando os candles mais bullish do mercado    
#==============================================================================
        for i in range(2,len(ticker['CLOSE'])):
            if close[i] > open_[i]:
                
                if close[i] == high[i]:
                    
                    if open_[i] == low[i]:
                        
                        bullish1.append(close[i])
                        bullish1Date.append[date[i]]
                    
                    else:
                        
                        bullish2.append(close[i])
                        bullish2Date.append(date[i])
                        
                if abs(close[i] - open_[i])/(high[i] - low[i]) <= .20: # percentual do corpo do candle em relação a sua sombra 
                    
                    bullish4.append(close[i])
                    bullish4Date.append(date[i])

                else:

                    if open_[i] == low[i]:

                        bullish5.append(close[i])
                        bullish5Date.append(date[i])
                    
                    else:

                        bullish3.append(close[i])
                        bullish3Date.append(date[i])
#==============================================================================
#==============================================================================

#==============================================================================
#         Identificando os candles mais bearish do mercado 
#==============================================================================

            if close[i] < open_[i]:
                
                if close[i] == low[i]:
                    
                    if open_[i] == high[i]:
                        
                        bearish1.append(close[i])
                        bearish1Date.append[date[i]]
                    
                    else:
                        
                        bearish2.append(close[i])
                        bearish2Date.append[date[i]]
                        
                if abs(close[i] - open_[i])/(high[i] - low[i]) <= .20: # percentual do corpo do candle em relação a sua sombra 
                    
                    bearish4.append(close[i])
                    bearish4Date.append[date[i]]
                    
                else:
                    
                    if open_[i] == high[i]:
                        
                        bearish5.append(close[i])
                        bearish5Date.append[date[i]]
                    
                    else:

                        bearish3.append(close[i])
                        bearish3Date.append[date[i]]        
#==============================================================================            
#==============================================================================
            if (open_[i-1] > close[i-1]) and (open_[i] < close[i]) and (open_[i] <= close[i-1]) and (close[i] > close[i-1] + 0.5*(open_[i-1] - close[i-1])):
                
                piercingDT.append(close[i])
                piercingDTDate.append(date[i])
                
            if (open_[i-1] > close[i-1]) and (open_[i] < close[i]) and (open_[i] <= close[i-1]) and (close[i] >= open_[i-1]):
                
                bullishEDT.append(close[i])
                bullishEDTDate.append(date[i])
                
            if (open_[i-1] > close[i-1]) and (open_[i] < close[i]) and (open_[i] > close[i-1]) and (close[i] < open_[i-1]):
                
                bullishHDT.append(close[i])
                bullishHDTDate.append(date[i])
                
            if (open_[i-1] < close[i-1]) and (open_[i] > close[i]) and (open_[i] >= close[i-1]) and (close[i] < close[i-1] - 0.5*(close[i] - open_[i-1])):
                
                dccUT.append(close[i])
                dccUTDate.append(date[i])
                
            if (open_[i-1] < close[i-1]) and (open_[i] > close[i]) and (open_[i] >= close[i-1]) and (close[i] <= open_[i-1]):
                
                bearishEUT.append(close[i])
                bearishEUTDate.append(date[i])
                
            if (open_[i-1] < close[i-1]) and (open_[i] > close[i]) and (open_[i] < close[i-1]) and (close[i] > open_[i-1]):
                
                bearishHUT.append(close[i])
                bearishHUTDate.append(date[i])
    
        bullish1 = pd.Series(bullish1, index = bullish1Date)
        bullish2 = pd.Series(bullish2, index = bullish2Date)
        bullish3 = pd.Series(bullish3, index = bullish3Date)
        bullish4 = pd.Series(bullish4, index = bullish4Date)
        bullish5 = pd.Series(bullish5, index = bullish5Date)
        
        bearish1 = pd.Series(bearish1, index = bearish1Date)
        bearish2 = pd.Series(bearish2, index = bearish2Date)
        bearish3 = pd.Series(bearish3, index = bearish3Date)
        bearish4 = pd.Series(bearish4, index = bearish4Date)
        bearish5 = pd.Series(bearish5, index = bearish5Date)
        
        piercingDT = pd.Series(piercingDT, index = piercingDTDate)
        bullishEDT = pd.Series(bullishEDT, index = bullishEDTDate)
        bullishHDT = pd.Series(bullishHDT, index = bullishHDTDate)
        
        dccUT = pd.Series(dccUT, index = dccUTDate)
        bearishEUT = pd.Series(bearishEUT, index = bearishEUTDate)
        bearishHUT = pd.Series(bearishHUT, index = bearishHUTDate)
        
        Indicator[eachStock] = {'PIERCINGDT': piercingDT,
                                'BULLISHEDT': bullishEDT,
                                'BULLISHHDT': bullishHDT,
                                'DARKCLOUD' : dccUT,
                                'BEARISHEUT': bearishEUT,
                                'BEARISHHUT': bearishHUT}
    
    return Indicator
         