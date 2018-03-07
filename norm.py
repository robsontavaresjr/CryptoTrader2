# -*- coding: utf-8 -*-
"""
Created on Tue May 03 20:39:49 2016

@author: Robson
"""
import numpy as np
import matplotlib.pyplot as plt

from pybrain.utilities           import percentError
from pybrain.datasets            import ClassificationDataSet
from pybrain.datasets            import SupervisedDataSet
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure           import FeedForwardNetwork
from pybrain.structure           import LinearLayer,TanhLayer,SoftmaxLayer
from pybrain.structure           import SigmoidLayer
from pybrain.structure           import FullConnection
from pybrain.structure           import RecurrentNetwork
 
def Norm(Slave,position = 0,box = 4, boxC = 7):
    
    order  = box*2    
    order2 = boxC*2
    
    stock  = Slave.database.keys()[position]
    ticker = Slave.database[stock]

    start2 = len(ticker['CLOSE']) % order2    

    close = np.array(ticker['CLOSE'])
    open_ = np.array(ticker['OPEN'])
    high  = np.array(ticker['HIGH'])
    low   = np.array(ticker['LOW'])    

    cI,cO,o,h,l      = [],[],[],[],[]    
    cIC,oC,hC,lC     = [],[],[],[]
    cOC = []
    
    for i in range(start2,len(close)-order2):

        cI.append((close[i+(boxC-box)+1:i+boxC+1])/close[i+boxC])
        cIC.append((close[i:i+boxC+1])/close[i+boxC])
        print " início: ", i
        print ' primeiro index numerador: ',  i+(boxC-box)
        print ' primeiro index denominador: ', i+boxC
        raw_input()
        
        o.append((open_[i+(boxC-box)+1:i+boxC+1])/close[i+boxC])
        oC.append((open_[i:i+boxC+1])/close[i+boxC])
        
        h.append((high[i+(boxC-box)+1:i+boxC+1])/close[i+boxC])
        hC.append((high[i:i+boxC+1])/close[i+boxC])

        l.append((low[i+(boxC-box)+1:i+boxC+1])/close[i+boxC])
        lC.append((low[i:i+boxC+1])-1/close[i+boxC])
        
        cO.append((close[i+boxC:i+(boxC+box)])/close[i+boxC])
        cOC.append((close[i:i+(boxC+box)])/close[i+boxC])
    
    return close,cI,cIC,cO
 
#==============================================================================
#                          Construção da Rede Neural
#==============================================================================

#    FNN = FeedForwardNetwork()
#    
#    inLayer     = LinearLayer(inputs)
#    hiddenLayer = SigmoidLayer(3)
#    outLayer    = SigmoidLayer(len(cO))
#    
#    in2hidden  = FullConnection(inLayer,hiddenLayer)
#    hidden2out = FullConnection(hiddenLayer,outLayer)
#
#    FNN.addConnection(in2hidden)
#    FNN.addConnection(hidden2out)

#==============================================================================
#                       Modelagem dos dados a serem inputados
#==============================================================================

    
#    alldata = SupervisedDataSet(inputs,len(cO[0]))
    geocI  = [[np.prod(cI[i]**(1./(box-1)))] for i in range(len(cI))]    
    geocIC = [[np.prod(cIC[i]**(1./(boxC)))] for i in range(len(cIC))]
    
    geocO  = [[np.prod(cO[i]**(1./(box-1)))] for i in range(len(cO))]
    geocOC = [[np.prod(cOC[i]**(1./(boxC)))] for i in range(len(cOC))]    
    
    alldata = ClassificationDataSet(26,5,nb_classes = 24)
        
    dataInput  = np.hstack((geocIC,cIC,geocI,cI,o,h,l))
    dataOutput = np.hstack((geocO,cO))
    

    for i in range(len(cI)):
         alldata.addSample(dataInput[i],dataOutput[i])
    
    tstdata,trndata = alldata.splitWithProportion(0.25)
    
    trndata._convertToOneOfMany()
    tstdata._convertToOneOfMany()
    
    fnn = buildNetwork(trndata.indim ,26, trndata.outdim ,outclass = SoftmaxLayer)
    
    trainer = BackpropTrainer(fnn, dataset=trndata, 
                              momentum = 0.1, 
                              verbose = True, 
                              weightdecay = 0.01)
#    
   

    trainer.trainEpochs(40)
        
    return cO,cI,o,h,l