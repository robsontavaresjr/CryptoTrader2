# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 13:12:49 2016

@author: Aluno - Joao
"""
import robotlib
import datetime
import data_handler_ID
import optlib
import copy
import numpy as np


############################################################################################################

def fixed_per(amount, maxrisk, rps):
    return amount * maxrisk / rps


############################################################################################################


def fractioned(current_wm, amount, F):
    qty = (amount * F) / current_wm['PRICE']

    return qty

############################################################################################################

def bet_all(amount, price):
    return amount / price

def optimalf(return_dict,leverage,optimizer_parameters = [100,500]):

    return_array = np.array(return_dict.values())
    number_of_stocks = len(return_dict.keys())

    def optimalfitness(fraction_list):
        
        fraction_array = np.array([fraction_list]).T
        p = 1. + (-1 * fraction_array * return_array / return_array.min(axis = 1)[np.newaxis].T)
        productory = np.prod(p,axis = 1)
        
        optimal = np.sum(productory)/number_of_stocks
        
        return optimal

    fraction_list_pso,best_fitness_pso = optlib.psoptimization(optimalfitness,number_of_stocks,max_or_min = 'max',particles=optimizer_parameters[0],iterations = optimizer_parameters[1],limit = [[0.,leverage] for i in range(number_of_stocks)],init_range = [0.,leverage])

    return fraction_list_pso

def optimalf_fitness(return_dict,leverage):

    return_array = np.array(return_dict.values())
    number_of_stocks = len(return_dict.keys())

    def fitness(fraction_list):
        
        fraction_array = np.array([fraction_list]).T
        p = 1. + (-1 * fraction_array * return_array / return_array.min(axis = 1)[np.newaxis].T)
        productory = np.prod(p,axis = 1)
        
        optimal = np.sum(productory)/number_of_stocks
        
        return optimal
    
    return fitness



    ############################################################################################################
def jaoptimalf(return_dict,leverage,optimizer_parameters = [100,500]):

    return_array = np.array(return_dict.values())
    
    columns = len(return_dict.values()[0])
    
    number_of_stocks = len(return_dict.keys())

    def optimalfitness(fraction_list):
        
        fraction_array = np.array([fraction_list])
        fraction_array = np.reshape(fraction_array,(number_of_stocks,columns))
        
        p = 1. + (-1 * fraction_array * return_array / return_array.min(axis = 1)[np.newaxis].T)
        productory = np.prod(p,axis = 1)
        
        optimal = np.sum(productory)/number_of_stocks
        
        return optimal
        
    dimension = number_of_stocks*columns
    
    print dimension
    
    fraction_list_pso,best_fitness_pso = optlib.psoptimization(optimalfitness,dimension,max_or_min = 'max',particles=optimizer_parameters[0],iterations = optimizer_parameters[1],limit = [[0.,leverage] for i in range(dimension)],init_range = [0.,leverage])

    return fraction_list_pso
