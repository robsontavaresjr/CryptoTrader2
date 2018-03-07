# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 16:12:33 2016

@author: jpsca1293
"""

import data_handler
import datetime
import tradex
import pickle
import robotlib
import risklib
import xlwings


if __name__ == '__main__':

    try:

        file_ = file('current_slave.pkl', 'r')
        trader = pickle.load(file_)
        file_.close()
        slave_on_dir = True

    except:

        slave_on_dir = False

    if not slave_on_dir:

        print 'Generating new slave.'

        stocks_file = file('stocks.txt', 'r')
        stocks = map(lambda x: x.replace('\n', ''), stocks_file.readlines())
        stocks_file.close()

        today = datetime.datetime.today()

        current_date = datetime.datetime(today.year, today.month, today.day)

        start_aq = current_date - datetime.timedelta(365)
        end_aq = current_date

        strategy_struct = tradex.read_kb('current_strategy.txt')

        database = data_handler.database_builder(stocks, start_aq, end_aq, source='google')
        indicators, working_days = data_handler.calculate_indicators(stocks, database,
                                                                     indicator_filter=strategy_struct[0])
        workmemory = data_handler.workmemory_builder(stocks)

        trader = robotlib.SlaveTrader(strategy_struct, working_days, initcash=50000, database=indicators)
        trader.update_portfolio_intention(workmemory)
        trader.set_brokerfee(14.9)
        trader.set_leverage(1.)

    else:

        print 'Using current_slave.pkl'

        stocks_file = file('stocks.txt', 'r')
        stocks = map(lambda x: x.replace('\n', ''), stocks_file.readlines())
        stocks_file.close()

        today = datetime.datetime.today()

        current_date = datetime.datetime(today.year, today.month, today.day)

        start_aq = current_date - datetime.timedelta(365)
        end_aq = current_date

        strategy_struct = trader.get_strategy_struct()

        database = data_handler.database_builder(stocks, start_aq, end_aq, source='google')
        indicators, working_days = data_handler.calculate_indicators(stocks, database,
                                                                     indicator_filter=strategy_struct[0])

        print 'Indicators calculated.'

        trader.set_database(indicators)
        trader.set_workingdays(working_days)

        workmemory = data_handler.workmemory_builder(stocks)

    if current_date <= trader.last_operational_date:

        print 'You have already operated in this date.'
        ans = input('Should I reprint your orders? 1 for yes 0 for no.')

        if ans:

            xlwings.Workbook()

            index = 1

            for stock in trader.operation_log.keys():

                xlwings.Range(1, (index, 1)).value = stock
                xlwings.Range(1, (index, 4)).value = 'OPERATION'
                xlwings.Range(1, (index, 5)).value = 'VOLUME'
                xlwings.Range(1, (index, 6)).value = 'PRICE'
                xlwings.Range(1, (index, 7)).value = 'INFERENCE'

                index += 1

                operations = trader.operation_log[stock]

                for operation in operations:

                    if operation['DATE'] == current_date:
                        operation_type = operation['OPERATION']
                        volume = operation['VOLUME']
                        price = operation['PRICE']
                        date = operation['DATE'].date()
                        inference = operation['INFERENCE']

                        xlwings.Range(1, (index, 1)).value = str(date)
                        xlwings.Range(1, (index, 4)).value = operation_type
                        xlwings.Range(1, (index, 5)).value = volume
                        xlwings.Range(1, (index, 6)).value = price
                        xlwings.Range(1, (index, 7)).value = inference

                        index += 1

                index += 1

            xlwings.Range(1, (index, 1)).value = 'AFTER TRANSACTIONS PORTFOLIO'

            for stock in trader.resumed_portfolio().keys():

                index +=1

                xlwings.Range(1, (index, 1)).value = stock
                xlwings.Range(1, (index, 2)).value = trader.resumed_portfolio()[stock]

    else:

        print 'Simulating ... please wait.'

        workmemory = data_handler.workmemory_feeder(workmemory, trader, current_date)
        trader.perform_orders(workmemory, current_date, risklib.optimalf)

        xlwings.Workbook()

        index = 1

        for stock in trader.operation_log.keys():

            xlwings.Range(1, (index, 1)).value = stock
            xlwings.Range(1, (index, 4)).value = 'OPERATION'
            xlwings.Range(1, (index, 5)).value = 'VOLUME'
            xlwings.Range(1, (index, 6)).value = 'PRICE'
            xlwings.Range(1, (index, 7)).value = 'INFERENCE'

            index += 1

            operations = trader.operation_log[stock]

            for operation in operations:

                if operation['DATE'] == current_date:

                    operation_type = operation['OPERATION']
                    volume = operation['VOLUME']
                    price = operation['PRICE']
                    date = operation['DATE'].date()
                    inference = operation['INFERENCE']

                    xlwings.Range(1, (index, 1)).value = str(date)
                    xlwings.Range(1, (index, 4)).value = operation_type
                    xlwings.Range(1, (index, 5)).value = volume
                    xlwings.Range(1, (index, 6)).value = price
                    xlwings.Range(1, (index, 7)).value = inference

                    index += 1

            index += 1

        xlwings.Range(1, (index, 1)).value = 'AFTER TRANSACTIONS PORTFOLIO'

        for stock in trader.resumed_portfolio().keys():
            index += 1

            xlwings.Range(1, (index, 1)).value = stock
            xlwings.Range(1, (index, 2)).value = trader.resumed_portfolio()[stock]

        file_ = file('current_slave.pkl','w')
        pickle.dump(trader, file_)
        file_.close()
