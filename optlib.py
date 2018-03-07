# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 11:18:33 2015

@author: jpsca1293
"""

import copy
import random
import numpy as np
import numpy.random as npr


def psoptimization(fitness, dimension, parameters=(0.74, 1.63, 1.63), iterations=1000, particles=70, init_range=(-1, 1),
                   limit=(float('-inf'), float('inf')), init_velocity=0.1, max_or_min='min', seed=None):
    '''  Particle Swarm Optimization algorithm.
    
    Function arguments:
        
        fitness - function to be minimized
        
        dimension - solution vector dimension
        
        parameters - algorithm parameters, in this order (iW,c1,c2) 
        Std - (0.74,1.63,1.63)
        
        iterations - number of iterative loops 
        Std - 1000 iterations
        
        particles - number of particles 
        Std - 70 particles
        
        InitRange - Population initialization range 
        Std - between (-1,1)
        
        InitVelocity - % of population initialization range 
        Std - 10% - 0.1
        
    '''

    # seed

    npr.seed(seed)

    # Initializing population



    # Parameters
    inertia_weight = parameters[0]
    alfa = (inertia_weight - 0.4) / iterations
    c1 = parameters[1]
    c2 = parameters[2]

    if len(limit) == dimension and type(limit[0]) == list:

        multilimit = True

    else:

        multilimit = False

    population = ((init_range[1] - init_range[0]) * npr.random((particles, dimension))) + init_range[0]

    pbest = copy.deepcopy(population)

    velocity = init_velocity * (
        ((init_range[1] - init_range[0]) * npr.random((particles, dimension))) + init_range[0])

    population_fitness = np.array(map(fitness, population))
    
    if max_or_min == 'min':

        
        gbest_fitness = min(population_fitness)
#        gbest = population[population_fitness.index(gbest_fitness)]
        gbest = population[population_fitness.argmin()]

    elif max_or_min == 'max':
        
        gbest_fitness = max(population_fitness)
#        gbest = population[population_fitness.index(gbest_fitness)]
        gbest = population[population_fitness.argmax()]

    pbest_fitness = copy.deepcopy(population_fitness)
    #population[population_fitness.index(gbest_fitness)]
    #population_fitness[np.where(np.isnan(population_fitness))] = min(population_fitness)

    # Iterations

    # Algorithm ~ Xt+1 = iW*Velocity + c1*Random*(Gbest - Xt) + c2*Random*(Pbest - Xt)

    for eachiteration in range(0, iterations):

        velocity = (inertia_weight * velocity) + c2 * npr.random((particles, dimension)) * (
            (gbest * np.ones((particles, 1))) - population) + c1 * npr.random((particles, dimension)) * (
            pbest - population)

        population += velocity

        if multilimit == False:

            population[population < limit[0]] = limit[0]
            population[population > limit[1]] = limit[1]

        elif multilimit == True:

            for i in range(dimension):
                valuecheck_upper = population[:, i] > limit[i][1]
                valuecheck_lower = population[:, i] < limit[i][0]

                population[valuecheck_upper == True, i] = limit[i][1]
                population[valuecheck_lower == True, i] = limit[i][0]

        population_fitness = np.array(map(fitness, population))

        # Update pbest and gbest

        for each in range(0, particles):

            if max_or_min == 'min':

                if population_fitness[each] < pbest_fitness[each]:

                    pbest[each] = population[each]
                    pbest_fitness[each] = population_fitness[each]

                    if pbest_fitness[each] < gbest_fitness:
                        gbest = pbest[each]
                        gbest_fitness = pbest_fitness[each]

            elif max_or_min == 'max':

                if population_fitness[each] > pbest_fitness[each]:

                    pbest[each] = population[each]
                    pbest_fitness[each] = population_fitness[each]

                    if pbest_fitness[each] > gbest_fitness:
                        gbest = pbest[each]
                        gbest_fitness = pbest_fitness[each]

        inertia_weight -= alfa

    return gbest, gbest_fitness


def gaoptimization(fitness, dimension, real_interval=None, bpd=30, pc=0.8, pm=0.1, n_population=100, iterations=1000,
                   elitism=True):
    def population_bin2real(binary_population, bits_per_dimension, intervals):

        real_population = []

        ds = []

        for interval in intervals:
            ds.append((interval[1] - interval[0]) / ((2. ** bits_per_dimension) - 1.))

        for binstr in binary_population:

            d = []

            last_index = 0
            for i in range(int(len(binstr) / bits_per_dimension)):
                bindiv = binstr[last_index:(i + 1) * bits_per_dimension]

                last_index = (i + 1) * bits_per_dimension

                mn = intervals[i][0]

                d.append(mn + ds[i] * int(bindiv, 2))

            real_population.append(d)

        return real_population

    # Population

    population = []

    for i in range(n_population):

        bstr = ''
        for eachDigit in range(0, dimension * bpd):
            bstr += str(random.randint(0, 1))

        population.append(bstr)

    if real_interval is not None:

        real_population = population_bin2real(population, bpd, real_interval)
        population_fitness = np.array(map(lambda x: fitness(x), real_population), np.float128)

    else:

        population_fitness = np.array(map(lambda x: fitness(x), population), np.float128)

    bestsofar = population[population_fitness.argmax()]
    bestsofarfit = max(population_fitness)

    operator_distribution = [pc, pc + pm]

    for eachIteration in range(iterations):

        probabilidades = []

        fmax = max(population_fitness)
        fmin = min(population_fitness)

        fitness_normalizada = ((population_fitness - fmin) / (fmax - fmin))
        sum_fn = sum(fitness_normalizada)

        probabilidades = fitness_normalizada / sum_fn

        distribuicao_probabilidades = []
        acumulador = 0.0

        for eachProb in probabilidades:
            distribuicao_probabilidades.append(acumulador + eachProb)
            acumulador += eachProb

        interm_population = []

        for upper_i in range(n_population):

            rpick = random.random()
            Cont = 0.0

            for i in range(len(distribuicao_probabilidades)):
                if rpick >= Cont and rpick < distribuicao_probabilidades[i]:
                    interm_population.append(copy.deepcopy(population[i]))
                Cont = distribuicao_probabilidades[i]

        new_population = []
        indexes_list = range(n_population)

        if elitism:
            new_population.append(bestsofar)
        else:
            pass

        while len(new_population) < n_population:

            index = indexes_list[random.randint(0, len(indexes_list) - 1)]
            indexes_list.pop(indexes_list.index(index))

            individual = interm_population[index]

            operation = random.random()

            if len(indexes_list) == 0:
                operation = pc + pm

            if (operation <= operator_distribution[0]):

                partner_index = indexes_list[random.randint(0, len(indexes_list) - 1)]
                indexes_list.pop(indexes_list.index(partner_index))

                partner = interm_population[partner_index]

                crossover_index = random.randint(1, (dimension * bpd) - 1)

                offspring1 = individual[0:crossover_index] + partner[crossover_index:]
                offspring2 = partner[0:crossover_index] + individual[crossover_index:]

                new_population.append(offspring1)
                new_population.append(offspring2)

            elif (operation > operator_distribution[0]) and (operation <= operator_distribution[1]):

                mutated_index = random.randint(0, (dimension * bpd) - 1)

                if individual[mutated_index] == '1':

                    if mutated_index == (dimension * bpd) - 1:

                        mutated_individual = individual[:mutated_index] + '0'

                    else:

                        mutated_individual = individual[:mutated_index] + '0' + individual[mutated_index + 1:]

                else:

                    if mutated_index == (dimension * bpd) - 1:

                        mutated_individual = individual[:mutated_index] + '1'

                    else:

                        mutated_individual = individual[:mutated_index] + '1' + individual[mutated_index + 1:]

                new_population.append(mutated_individual)

            else:

                new_population.append(individual)

        if real_interval is not None:

            real_population = population_bin2real(new_population, bpd, real_interval)
            new_population_fitness = np.array(map(lambda x: fitness(x), real_population), np.float128)

        else:

            new_population_fitness = np.array(map(lambda x: fitness(x), new_population), np.float128)

        population = new_population
        population_fitness = new_population_fitness

        current_population_best = population[population_fitness.argmax()]
        current_population_best_fitness = max(population_fitness)

        if current_population_best_fitness > bestsofarfit:

            bestsofar = current_population_best
            bestsofarfit = current_population_best_fitness

            #print 'Max: ', bestsofarfit

        if all(np.equal(population_fitness, max(population_fitness))):
            print 'Full convergence'
            break

    if real_interval is None:
        return bestsofar,bestsofarfit
    else:
        return np.array(population_bin2real([bestsofar],bpd,real_interval)[0]),bestsofarfit
