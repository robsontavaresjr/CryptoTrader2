# -*- coding: utf-8 -*-
"""
Created on Thu May 05 16:23:29 2016

@author: Suporte
"""
import numpy as np

def taAnalyst(indicators,Slave,timeFrame = 3):
    
    Trend = {}
    bullish = ['BULLISHHDT','BULLISHEDT']
    bearish = ['BEARISHHUT','BEARISHEUT']
    
    for eachStock in indicators.keys():

        close = Slave.database[eachStock]['CLOSE']
        open_ = Slave.database[eachStock]['OPEN']
        high  = Slave.database[eachStock]['HIGH']
        low   = Slave.database[eachStock]['LOW']
        
        for eachIndicator in indicators[eachStock].keys():
            
            dateList = indicators[eachStock][eachIndicator].index
            before   = []
            after    = []
            answer   = []
            
            for finder in range(len(dateList)):
                
                centralDate = dateList[finder].to_datetime()
                
                b  = np.array(close[list(close.index).index(centralDate) - timeFrame:
                           list(close.index).index(centralDate)])/close[centralDate]
                
                a  = np.array(close[list(close.index).index(centralDate) + 1:
                           list(close.index).index(centralDate) + timeFrame + 1])/close[centralDate]
                           
                
                before.append(np.prod(b)**(1./timeFrame))
                after.append(np.prod(a)**(1./timeFrame))
                
                if eachIndicator in bullish:
                    
                    if np.prod(b)**(1./timeFrame) < np.prod(a)**(1./timeFrame):
                        answer.append(1)
                    else:
                        answer.append(0)
                else:
                    
                    if np.prod(b)**(1./timeFrame) > np.prod(a)**(1./timeFrame):
                        answer.append(1)
                    else:
                        answer.append(0)
                        
            precision_rate = float(answer.count(1))/len(answer)
            
            Trend[eachStock + '_' + eachIndicator] = precision_rate
            
    return Trend
            