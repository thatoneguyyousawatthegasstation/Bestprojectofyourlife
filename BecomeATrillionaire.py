import dask.array as da
import dask.dataframe as dd
import numpy as np
import os
import dask
import datetime
from dask.diagnostics import ProgressBar
import plotly.graph_objects as go
import pandas as pd
import plotly
from lenspy import DynamicPlot
from plotly.subplots import make_subplots
import pandas_datareader as pdr

# make tbarcount into global function requiring dataframe and latching onto the global for loop
# make a function to put indicators into dataframe
# make width a global variable that attaches to the indicator tbar number, rather than tbar_count
# make tbar_number function global

# give each trade and indicator its own undentifier number, loop the trade manager between identifiers


start_balance = 10000
current_equity = start_balance
max_equity = start_balance
current_price = 0
long_entry_price = 0
short_entry_price = 0
CAGR_window = 0
CAGR_mean_dd_value = 0
xoverpip = 0
long_entry = False
short_entry = False
direction = "none"
tbar_count = 0
trade_ID = 0
trade_ID_tracker = []

df = pd.read_csv(r'C:\EURUSD_mt5_ticks.csv', parse_dates=['Date'])

df.columns = ['Date', 'Ask_Price', 'Ask_Volume', 'Bid_Price', 'Bid_Volume', 'Spread']

df['Date'] = dd.to_datetime(df['Date'].astype('datetime64[ns]'), exact=True, cache=True, format='%Y-%m-%d  %H:%M:%S.%f')

MA1 = df['Ask_Price'].rolling(4).mean()

MA2 = df['Ask_Price'].rolling(21).mean()

#////////////////////////////////////////////////////////////////////

# Create dictionary to keep track of trade IDs and trade directions
class trade_dict(dict):

    # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value


# Main Function
trade_dict = trade_dict()


# /////////////////////////////////////////////////////////////////

# Create a list of trade IDs currently in deployment
def init_trade_ID():
    trade_ID = trade_ID + 1
    trade_dict.add(trade_ID, direction)

    trade_ID_tracker.append(trade_ID)


#         delete trade ID after close trade

# updates profit for each open trade
#
#////////////////////////////////////////////////////////////////////

def trade_manager(TP, SL):
    if len(trade_dict) == 0:
        pass
    if len(trade_dict) > 0:

        # keeps track of current profit in pips for each open trade
        for i in trade_ID_tracker:
            trade_dict[i] = current_price - long_entry_price

               # if price hits take profit point, close trade and calculate profits
           if long_entry == True & (current_price - long_entry_price >= TP):
               current_equity += current_price - long_entry_price * 10000  # for backtesting purposes only
               long_entry = False
               close_trade(trade_ID, "long")
               # send exit signal to mt5

               # take profit at 5 pips on Short
           if short_entry == True & (current_price - short_entry_price <= 0 - (TP)):
               current_equity += 0 - current_price - short_entry_price * 10000  # for backtesting purposes only
               short_entry = False
        
               # send exit signal to mt5


current_price = df.loc[tbar_count, 'Ask_Price']  # find out proper price method
Current_balance = 10000
currency = "EURUSD"

#////////////////////////////////////////////////////////////////////

# direction[long, short], TP[float in pips], risk[float in percent], SL[ float in pips]
def enter_trade(direction, TP, risk, SL):
    TP = enter_trade(TP)

    # make into a class to reference these
    pip_value = 0
    SL_price = 0

    # TP in true pips
    TP_pips = TP / 10000

    # TP in dollars
    TP_value = TP_pips * 10000

    # SL in true pips
    SL_pips = SL / 10000

    # SL in dollars
    SL_value = SL_pips * 10000

    # 1 pip = 0.0001 points (out of 1.00000)
    # pips converted to true value
    pips = 1 / 10000

    # risk % converted to true value in dollars
    risk_value = Current_balance * (risk * 0.01)

    if direction == "long":
        long_entry = True
        long_entry_price = df.loc[tbar_count, 'Ask_Price']  # find out proper price method
        # send trade signal to mt5
        init_trade_ID()

        SL_price = current_price - pips

    if direction == "short":
        short_entry = True
        short_entry_price = df.loc[tbar_count, 'Ask_Price']  # find out proper price method
        # send trade signal to mt5
        init_trade_ID()
        SL_price = current_price + pips

    quote_currency = currency[:-3]

    # pip value of standard lot = $10 if quote(second)currency is USD
    # if quote currency is USD, use normal lot values
    if quote_currency == "USD":
        pip_value = lot_size * 10

    # pip value of standard lot = $10 x quote currency of USD/* if the traded quote currency is not USD
    # if quote currency is not USD, use adjusted lot values
    if quote_currency != "USD":
        pip_value = lot_size * (10 * current_price)

    # risk calc = SL value in dollars * pip value in dollars / risk value in dollars
    # number of lots to be traded based on input paramters
    trade_lots = SL_pips * pip_value / risk_value

#////////////////////////////////////////////////////////////////////

# trade idenfiication number, direction filter[filters closes by direction[long, short. both]]
def close_trade(trade_ID, direction_filter):
    if direction_filter == 'long' in trade_ID:
        current_equity += current_price - long_entry_price * 10000  # for backtesting purposes only
        long_entry = False
        # delete trade ID from dict
        trade_dict.pop(trade_ID)

        # delete trade ID from trade ID tracker
        trade_ID_tracker.pop(trade_ID)

        # send exit signal to mt5

    if direction_filter == 'short' in trade_ID:
        current_equity += 0 - current_price - short_entry_price * 10000  # for backtesting purposes only
        short_entry = False
        # delete trade ID from dict
        trade_dict.pop(trade_ID)

        # delete trade ID from trade ID tracker
        trade_ID_tracker.pop(trade_ID)

        # send exit signal to mt5

    if direction_filter == 'both' in trade_ID:
        if short_entry == True:
            current_equity += 0 - current_price - short_entry_price * 10000  # for backtesting purposes only
            short_entry = False

            # delete trade ID from dict
            trade_dict.pop(trade_ID)

            # delete trade ID from trade ID tracker
            trade_ID_tracker.pop(trade_ID)
            # send exit signal to mt5

        if long_entry == True:
            current_equity += current_price - short_entry_price * 10000  # for backtesting purposes only
            long_entry = False

            # delete trade ID from dict
            trade_dict.pop(trade_ID)

            # delete trade ID from trade ID tracker
            trade_ID_tracker.pop(trade_ID)
            # send exit signal to mt5

#////////////////////////////////////////////////////////////////////


import operator
ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,  # use operator.div for Python 2
    '%': operator.mod,
    '^': operator.xor,
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '>': operator.gt
}



def tbar_number(n):
    return tbar_count - n


# variable1_column, direction(<, <=, ==, >=, >), variable2_column, data, variable1_column, variable2_column, width
# variable1_column and variable2_column are the column names of the variables to be measured within the dataframe
# direction is the comparative operator
# vdataframe is the name of the dataframe that contains the variable data
# width is the number of bars in the past the cross must happen in order for it to count

#////////////////////////////////////////////////////////////////////

previous_cross = 'both'

def vcross(variable1_column, direction, variable2_column, vdataframe, width):
    width_value = tbar_number(width)

    for i in range(width_value + 1):
        width_value_count = (-(i))
        for v1_width_data, v2_width_data in df.loc[width_value_count, variable1_column], df.loc[
            width_value_count, variable2_column]:

            if direction == ">=" | ">" & ops[direction](v1_width_data,
                                                        v2_width_data) & previous_cross == 'short' | 'both':
                if direction == ">=" and v1_width_data == v2_width_data:
                    return True
                if direction == ">":
                    previous_cross = 'long'
                    return True

            if direction == "<=" | "<" & ops[direction](variable1, variable2) & previous_cross == 'long' | 'both':
                if direction == "<=" and v1_width_data == v2_width_data:
                    return True
                if direction == "<":
                    previous_cross = 'short'
                    return True

            if direction == "==" & ops[direction](variable1, variable2):
               return True
#////////////////////////////////////////////////////////////////////
 
    
#somehow get it all to work together
for tbar_count in range(len(df)):
    trade_manager(5, 20)
    if vcross(MA1, ">", MA2, df, 1):
        enter_trade(long, 5, 1, 20)


#Evil error:
# KeyError: "None of [Float64Index([               nan,                nan,                nan,\n                        1.171995,              1.172,              1.172,\n                        1.172005, 1.1720074999999999, 1.1720074999999999,\n                        1.172005,\n              ...\n                         1.17031,          1.1703025,          1.1702975,\n              1.1702949999999999,             1.1703,          1.1702925,\n                         1.17029, 1.1702875000000001,           1.170285,\n                         1.17029],\n             dtype='float64', length=234904)] are in the [index]"
#sadness.
