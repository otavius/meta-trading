import warnings 
from datetime import datetime 
import pandas as pd 
import MetaTrader5 as mt5
warnings.filterwarnings("ignore")
mt5.initialize()



class MT5:

    def get_data(symbol, n, timeframe=mt5.TIMEFRAME_D1):
        """ Function to import the data of the chosen symbol"""

        # Initialize the connection if there is not 
        mt5.initialize()

        # current date extract 
        utc_from = datetime.now()

        # Import the data into a tuple 
        rates = mt5.copy_rates_from(symbol, timeframe, utc_from, n)

        # Tuple to dataframe 
        rates_frame = pd.DataFrame(rates)

        # Convert tie in seconds into the datetime format
        rates_frame["time"] = pd.to_datetime(rates_frame['time'], unit="s")

        # Convert the column "time" in the right format 
        rates_frame["time"] = pd.to_datetime(rates_frame["time"], format="%y-%m-%d")

        # set column time as the index of the datetime 
        rates_frame = rates_frame.set_index("time")
        return rates_frame
    
    def orders(symbol, lot, buy=True, id_position=None):
        """ Send the orders """

        # Initialize the connection if there is not 
        if mt5.initialize() == False:
            mt5.initialize()

        # Filling order mode (need to try 0, 1, 2)
        # because it is depending of the broker 
        i = 1

        # Take ask price 
        ask_price = mt5.symbol_info_tick(symbol).ask 

        # Take bid price 
        bid_price = mt5.symbol_infO_tick(symbol).bid 

        # Take the point of the asset 
        point = mt5.symbol_info(symbol).point

        deviation = 20 # mt5.getSlippage(symbol)
        #************************************ Open a trade **********************************
        if id_position == None:
            # Buy order Parameters
            if buy:
                type_trade = mt5.ORDER_TYPE_BUY
                sl = ask_price - 100 * point
                tp = ask_price + 100 * point 
                price = ask_price 

            # Sell order parameters 
            else: 
                type_trade = mt5.ORDER_TYPE_SELL
                sl = bid_price + 100 * point 
                tp = bid_price - 100 * point 
                price = bid_price

            # open the trade 
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": type_trade,
                "price": price,
                "deviation": deviation,
                "sl": sl,
                "tp": tp,
                "magic": 191954,
                "comment": "python script order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": i,
            }
            # send a trading request 
            result = mt5.order_send(request)
            result_comment = result.comment

        #**************** Close a trade *****************************************
        else: 
            # Buy order parameters 
            if buy:
                type_trade = mt5.ORDER_TYPE_SELL
                price = bid_price
            # Sell order parameters
            else:
                type_trade = mt5.ORDER_TYPE_BUY
                price = ask_price 

            # close the trade 
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": type_trade,
                "position": id_position,
                "price": price,
                "deviation": deviation,
                "magic": 191954,
                "comment": "python script order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": i,
            }
            # send a trading request
            result = mt5.order_send(request)
            result_comment = result.comment
        return result.comment

    def resume():
        """ Return the current positions. Position=0 ---> BUY """
        # initialize the connection if there is not 
        mt5.initialize()

        # Define the name of the columns that we will create 
        colonnes = ["ticket", "position", "symbol", "volume"]

        # Go take the current open trades 
        current = mt5.positions_get()

        # Create a empty dataframe 
        summary = pd.DataFrame()

        # loop to add each row in dataframe 
        # (can be ameliorate using of list of list)
        for element in current:
            element_pandas = pd.DataFrame([element.ticket, element.type, element.symbol, element.volume], index=colonnes).transpose()
            summary = pd.concat((summary, element_pandas), axis=0)
        return summary
    
    def run(symbol, long, short, lot):
        # Initialize the connection if there is not 
        if mt5.initialize() == False:
            mt5.initialize()

        # Choose your symbol
        print("-----------------------------------------")
        print("Date: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("SYMBOL: ", symbol)

        # Initialize the device 
        current_open_positions = MT5.resume()
        # Buy or Sell 
        print(f"Buy: {long} \t Short: {short}")

        """ close trade eventually"""
        