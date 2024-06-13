import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

buy_types = [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_STOP_LIMIT]
buy_types = [mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP, mt5.ORDER_TYPE_SELL_STOP_LIMIT]

class mt5_client: #Connection to MT5 client
    def __init__(self, path):
        # Establish the MT5 terminal
        mt5.initialize(path)

    def connect(self, account):
        self.account = account
        self.__login = account['login']
        self.__pwd = account['password']
        self.__server = account['server']
        authorized=mt5.login(server=self.__server, login=self.__login, password=self.__pwd)

        if authorized:
            print("Connected to MT5 Client")
        else:
            print("Failed to connect at account #{}, error code: {}"
                .format(self.__login, mt5.last_error()))
            self.authorized = False
            return
        
        self.initial_balance = self.account['capital']
        self.day_balance = float(mt5.account_info().balance)
        self.last_trade_day = datetime.utcnow().strftime("%Y%m%d")
        self.open_balance = mt5.account_info().balance
        print("Initial Balance:", self.open_balance)

        self.max_dd = self.account['max_dd']
        self.max_daily_dd = self.account['daily_dd']

        algo_trading = mt5.terminal_info().trade_allowed
        if algo_trading == True:
            print("Algo Trading ENABLED")
            self.authorized = True
        else:
            print("Algo Trading DISABLED")
            self.authorized = False

        return

    def disconnect(self):
        mt5.shutdown()
        self.authorized=False
        print("Disconnected from MT5 Client")

    ## positions always need to have a SL and TP
    def open_position(self, pair, order_type, size, tp=None, sl=None, tp_dist=None, sl_dist=None, comment=""):
        #TODO: Fix position entry fails to open when symbol not visible
        risk_ok = True
        symbol_info = mt5.symbol_info(pair)
        if symbol_info is None:
            print(pair, "not found")
            return

        if not symbol_info.visible:
            print(pair, "is not visible, trying to switch on")
            if not mt5.symbol_select(pair, True):
                print("symbol_select({}}) failed, exit",pair)
                return
        print(pair, "found!")

        point = symbol_info.point
        
        if(order_type == "BUY"):
            order = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(pair).ask
            # if tp and sl, check if sl is less than sl dist, then use it
            # this means that sl_dist is always the max risk
            # means always should have an sl_dist and tp_dist - NOT TRUE
            # if no tp/sl, use tp/sl dist
            calc_sl = price - (sl_dist * point)
            calc_tp = price + (tp_dist * point)

            if (sl): sl = max(calc_sl, sl)
            else: sl = calc_sl
            if (tp): tp = min(calc_tp, tp)
            else: tp = calc_tp
                
        if(order_type == "SELL"):
            order = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(pair).bid
            calc_sl = price + (sl_dist * point)
            calc_tp = price - (tp_dist * point)
            
            if (sl): sl = min(calc_sl, sl)
            else: sl = calc_sl
            if (tp): tp = max(calc_tp, tp)
            else: tp = calc_tp


        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": float(sl),
            "tp": float(tp),
            "magic": 234000,
            "comment": str(comment),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        risk = mt5.order_calc_profit(order, pair, float(size), float(price), float(sl))
        risk_ok = self.calc_risk(risk, symbol=pair)

        if risk_ok == True:
            result = mt5.order_send(request)
        else:
            result = lambda : None
            result.retcode = 0
            result.comment = "Risk exceeds max daily drawdown"

        #TODO: Retry sending order if invalid stops/invalid price etc.
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to send order:", result)
        else:
            print("Order successfully placed!")
        return result

    def open_pending(self, pair, order_type, size, price, tp=None, sl=None, tp_dist=None, sl_dist=None, comment=""):
        risk_ok = True
        action = mt5.TRADE_ACTION_PENDING
        symbol_info = mt5.symbol_info(pair)
        if symbol_info is None:
            print(pair, "not found")
            return

        if not symbol_info.visible:
            print(pair, "is not visible, trying to switch on")
            if not mt5.symbol_select(pair, True):
                print("symbol_select({}}) failed, exit",pair)
                return
        print(pair, "found!")

        point = symbol_info.point
        price = float(price)
        
        if(order_type == "BUY"):
            dir = mt5.ORDER_TYPE_BUY
            current_price = mt5.symbol_info_tick(pair).ask
            # if pending price is within 1 point of current price, market order to avoid missing plays. 
            # TODO: decide if this is worth keeping. results in entering positions before alert, play might not yet be valid
            # could add directionality, so that you only convert to market entry if it would have been a limit order not a stop order
            # this would prevent missing plays because of late alert, but would prevent entering position early
            #if abs(current_price - price) < 1:
            #    order = mt5.ORDER_TYPE_BUY
            #    action = mt5.TRADE_ACTION_DEAL
            #    price = current_price
            if current_price - price > 0:
                order = mt5.ORDER_TYPE_BUY_LIMIT
            else:
                order = mt5.ORDER_TYPE_BUY_STOP

            calc_sl = price - (sl_dist * point)
            calc_tp = price + (tp_dist * point)

            if (sl): sl = max(calc_sl, sl)
            else: sl = calc_sl
            if (tp): tp = min(calc_tp, tp)
            else: tp = calc_tp
                
        if(order_type == "SELL"):
            dir = mt5.ORDER_TYPE_SELL
            current_price = mt5.symbol_info_tick(pair).bid
            # if pending price is within 1 point of current price, market order to avoid missing plays
            #if abs(current_price - price) < 1:
            #    order = mt5.ORDER_TYPE_SELL
            #    action = mt5.TRADE_ACTION_DEAL
            #    price = current_price
            if current_price - price < 0:
                order = mt5.ORDER_TYPE_SELL_LIMIT
            else:
                order = mt5.ORDER_TYPE_SELL_STOP

            calc_sl = price + (sl_dist * point)
            calc_tp = price - (tp_dist * point)
            
            if (sl): sl = min(calc_sl, sl)
            else: sl = calc_sl
            if (tp): tp = max(calc_tp, tp)
            else: tp = calc_tp

        request = {
            "action": action,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": float(sl),
            "tp": float(tp),
            "magic": 234000,
            "comment": str(comment),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        risk = mt5.order_calc_profit(dir, pair, float(size), float(price), float(sl))
        risk_ok = self.calc_risk(risk, symbol=pair)
        print("Price:", price, "SL:", sl)

        if risk_ok == True:
            result = mt5.order_send(request)
        else:
            result = lambda : None
            result.retcode = 0
            result.comment = "Risk exceeds max daily drawdown"

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to send order:", result)
        else:
            print("Order successfully placed!")
        return result

    def positions_get(self, symbol=None):
        if(symbol is None):
            res = mt5.positions_get()
        else:
            res = mt5.positions_get(symbol=symbol)

        if(res is not None and res != ()):
            df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        
        return pd.DataFrame()

    def orders_get(self, symbol=None):
        if(symbol is None):
            res = mt5.orders_get()
        else:
            res = mt5.orders_get(symbol=symbol)

        if(res is not None and res != ()):
            df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
            return df
        
        return pd.DataFrame()

    def modify_position(self, deal_id, symbol, tp=None, sl=None, tp_dist=None, sl_dist=None, comment=""):
        risk_ok = True
        positions = self.positions_get()
        if positions.empty == True: open_positions = self.orders_get()
        else: open_positions = positions
        open_positions = open_positions[open_positions['ticket'] == deal_id]
        order_type = open_positions['type'].iloc[0]
        symbol = open_positions['symbol'].iloc[0]
        if positions.empty == True: 
            size = open_positions['volume_current'].iloc[0]
            action = mt5.TRADE_ACTION_MODIFY
        else: 
            size = open_positions['volume'].iloc[0]
            action = mt5.TRADE_ACTION_SLTP
        price = open_positions['price_open'].iloc[0]
        point = mt5.symbol_info(symbol).point

        modify_request={
            "action": action,
            "symbol": symbol,
            "magic": 234000,
            "comment": comment
        }

        if positions.empty == True: 
            modify_request["order"] = int(deal_id)
            modify_request["price"] = float(price)
        else: modify_request["position"] = int(deal_id)

        if(tp): modify_request["tp"] = float(tp)
        elif(tp_dist):
            if order_type == mt5.ORDER_TYPE_BUY or order_type == mt5.ORDER_TYPE_BUY_LIMIT or order_type == mt5.ORDER_TYPE_BUY_STOP:
                tp = price + (tp_dist * point)
            elif order_type == mt5.ORDER_TYPE_SELL or order_type == mt5.ORDER_TYPE_SELL_LIMIT or order_type == mt5.ORDER_TYPE_SELL_STOP:
                tp = price - (tp_dist * point)
            modify_request["tp"] = float(tp)
        else:
            # no tp, don't sent order
            result = lambda : None
            result.retcode = 0
            result.comment = "No TP provided to modify order"
            return result

        if(sl): 
            if order_type == mt5.ORDER_TYPE_BUY or order_type == mt5.ORDER_TYPE_BUY_LIMIT or order_type == mt5.ORDER_TYPE_BUY_STOP:
                if sl_dist != None:
                    calc_sl = price - (sl_dist * point)
                    sl = max(calc_sl, sl)
                order_type = mt5.ORDER_TYPE_BUY
            elif order_type == mt5.ORDER_TYPE_SELL or order_type == mt5.ORDER_TYPE_SELL_LIMIT or order_type == mt5.ORDER_TYPE_SELL_STOP:
                if sl_dist != None:
                    calc_sl = price + (sl_dist * point)
                    sl = min(calc_sl, sl)
                order_type = mt5.ORDER_TYPE_SELL
            
            risk = mt5.order_calc_profit(int(order_type), symbol, float(size), float(price), float(sl))
            risk_ok = self.calc_risk(risk, symbol=symbol)
            modify_request["sl"] = float(sl) # move to end of if sl
            
        elif(sl_dist):
            if order_type == mt5.ORDER_TYPE_BUY or order_type == mt5.ORDER_TYPE_BUY_LIMIT or order_type == mt5.ORDER_TYPE_BUY_STOP:
                #TODO: Fix to match if(sl): so that bad sl_distances can be caught
                sl = price - (sl_dist * point)
                order_type = mt5.ORDER_TYPE_BUY
            elif order_type == mt5.ORDER_TYPE_SELL or order_type == mt5.ORDER_TYPE_SELL_LIMIT or order_type == mt5.ORDER_TYPE_SELL_STOP:
                sl = price + (sl_dist * point)
                order_type = mt5.ORDER_TYPE_SELL

            risk = mt5.order_calc_profit(int(order_type), symbol, float(size), float(price), float(sl))
            risk_ok = self.calc_risk(risk, symbol=symbol)
            modify_request["sl"] = float(sl) # move to end of if sl

        else:
            #no sl, don't send order
            # no tp, don't sent order
            result = lambda : None
            result.retcode = 0
            result.comment = "No SL provided to modify order"
            return result

        if risk_ok == True:
            result = mt5.order_send(modify_request)
        else:
            result = lambda : None
            result.retcode = 0
            result.comment = "Risk exceeds max daily drawdown"
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to modify order:", result)
        else:
            print("Order successfully modified!")
        return result

    def close_position(self, deal_id, volume=None, comment=""):
        open_positions = self.positions_get()
        if open_positions.empty == True: return
        position = open_positions[open_positions['ticket'] == deal_id]
        order_type = position['type'].iloc[0]
        symbol = position['symbol'].iloc[0]
        symbol_info = mt5.symbol_info(symbol)

        if volume == None:
            volume = position['volume'].iloc[0]
        else:
            volume = symbol_info.volume_step * (1 + float(volume) // symbol_info.volume_step)

        if(order_type == mt5.ORDER_TYPE_BUY):
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        
        close_request={
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "position": deal_id,
            "price": price,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(close_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to close order:", result)
        else:
            print("Order successfully closed!")
        return result

    def close_positions_by_symbol(self, symbol):
        open_positions = self.positions_get(symbol)
        if open_positions.empty == False:
            open_positions['ticket'].apply(lambda x: self.close_position(x)) # TODO: This is cool, figure out how this works
            msg = str("Closed all %s positions" % symbol)
        else:
            msg = "No open positions under this ticker!"
        print(msg)
        return msg 

    def close_orders_by_symbol(self, symbol):
        open_orders = self.orders_get(symbol)
        if open_orders.empty == False:
            open_orders['ticket'].apply(lambda x: self.remove_pending(x)) # TODO: This is cool, figure out how this works
            if symbol == None: symbol = ""
            msg = str("Closed all pending %s orders" % symbol)
        else:
            msg = "No open pending orders under this ticker!"
        print(msg)
        return msg 
        
    def remove_pending(self, order_id):
        close_request={
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order_id,
        }
        result = mt5.order_send(close_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to close order:", result)
        else:
            print("Order successfully closed!")
        return result
    
    #TODO: check to make sure symbol name is correct, used only for getting current time data
    def calc_risk(self, stopout, symbol="XAUUSD+"):
        account_balance = float(mt5.account_info().balance)
        time = mt5.symbol_info(symbol).time
        date = datetime.utcfromtimestamp(time).strftime("%Y%m%d")

        if date != self.last_trade_day: # if new day, reset max daily dd to current balance
            self.last_trade_day = date
            self.day_balance = account_balance
            print("Prev. Date:", self.last_trade_day, "Today:", date)
        else: #positions have been opened today, calculate pnl + dd
            print("!E! Prev. Date:", self.last_trade_day, "Today:", date)
            pass

        open_positions = self.positions_get()
        #open_orders = self.order_get() # may need to account for pending orders in the future
        #probably don't need to bother if only one order/position can be open at a time
        
        dd = 0
        for index, position in open_positions.iterrows():
            sl = abs(float(position['price_open']) - float(position['sl'])) #try printing this to make sure it's correct
            risk = float(mt5.symbol_info(position['symbol']).point)*float(position['volume']) #try printing this to make sure it's correct
            dd += risk*sl
        #for index, order in open_orders.iterrows():
            #risk = abs(order['price_open'] - order['sl'])*mt5.symbol_info(order['symbol']).point*order['volume_current']
            #dd += risk
        print(account_balance, dd, stopout, self.day_balance, self.max_daily_dd)
        if account_balance - dd - abs(stopout) <= self.day_balance - self.max_daily_dd:
            #Risk exceeds max allowed daily dd
            return False
        #TODO: CHANGE DAY_BALANCE BACK TO INITIAL_BALANCE WHEN GOING LIVE
        # Done, going live
        elif account_balance - dd - abs(stopout) <= self.initial_balance - self.max_dd:
            #Risk exceeds max allowed dd
            return False
        else:
            return True

    def get_price(self, symbol):
        #TODO: retrieve some data about a symbol, price, etc
        return mt5.symbol_info_tick(symbol).bid, mt5.symbol_info_tick(symbol).ask