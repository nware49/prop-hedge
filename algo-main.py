import threading
import pandas as pd
import numpy as np
import time
import schedule
# import client
import accounts
import tradeschedule
import asyncio
import datetime
import random
import functools

filename = 'acc-creds.json'

# Create a class for handling accounts on MetaTrader5, DXTrade, and TradeLocker
class AccountManager(threading.Thread):
    def __init__(self):
        super().__init__()
        # One single MT5 connection should be established for each thread and used by all MT5 accounts
        #self.mt5_client = None
        # Name of the account the thread is currently connected to
        self.account_name = None
    
    # Refactor to initialize a MT5 connection on both threads on startup
    # Then connect to platform each time you want to place a trade
    # No real urgency, don't need to worry about time spent logging in
    
    def connect(self, account_name, version):
        # Get account
        self.account = accounts.fetch_account_data(filename, account_name)
        self.account_name = account_name

        # Determine which platform to connect to
        platform = self.account['platform']
        # TODO: Condense to lookup table?
        if platform == "MT5": # Connect to MT5 client manager
            # Create a connection to the MT5 terminal which can be utilized by the account manager thread
            self.client = accounts.connect_MT5(self.account, version)
            # Check if connection is authorized
            if self.client.authorized == False:
                quit(code="MT5 account unauthorized.")
            #if self.mt5_client == None: self.mt5_client = self.client #TODO: Fix this. Meh its okay.
        elif platform == "DXTrade": # Connect to DXTrade with ____ request
            self.client = 0
        elif platform == "TradeLocker": # TODO: Not sure how to connect yet
            self.client = 0
        else: # Unsupported platform, return failed connection
            self.client = 0
        
        if self.client == 0: return 0 # Failed to connect to platform, return

    def calc_volume(self, price=None, tp=None, sl=None):
        #points_won = tp - price
        #points_lost = sl - price
        # Need to know how many dollars can be lost per trade
        symbol_info = self.client.get_symbol_info(self.account["symbol"])
        acc_size = self.account["capital"]
        trade_dd = self.account["trade_dd"]
        allowed_loss = acc_size * trade_dd # Conservative loss amount in dollars, not maximum for breach
        print("LOG: %s can lose $%f per trade" % (self.account_name, allowed_loss))
        # Calculate points
        points = self.account["trade_points"] * symbol_info.trade_contract_size
        # Calculate position size
        volume = allowed_loss / points
        print("LOG: %s volume pre-round" % volume)
        # Probably need to round down to 2 decimals TODO: adjust for all currencies not just XAUUSD
        volume = int(100 * volume) / 100
        print("LOG: %s volume post-round" % volume)
        # Do a check to make sure this makes sense
        check_volume = self.client.order_calc_profit(0, self.account["symbol"], volume, symbol_info.bid, symbol_info.bid+self.account["trade_points"])
        print("LOG: %f calculated profit check vs. allowed profit %f" % (check_volume, allowed_loss))
        # Check to see that one is not truncated

        return volume
    
    def open_pos(self, side):
        # def open_position(self, pair, order_type, size, tp=None, sl=None, tp_dist=None, sl_dist=None, comment=""):
        pair = self.account['symbol']
        symbol_info = self.client.get_symbol_info(pair)
        order_type = side
        size = self.calc_volume()
        tp_dist = self.account['trade_points'] * symbol_info.trade_contract_size
        sl_dist = self.account['trade_points'] * symbol_info.trade_contract_size
        result = self.client.open_position(pair, order_type, size, tp_dist=tp_dist, sl_dist=sl_dist)

        return result
    
    def close_pos(self):
        # Should only be one position open, so closing all of them is okay
        self.mt5_client.close_positions_by_symbol(self.account[1]['symbol'])


class CentralThread(threading.Thread):
    def __init__(self, client1, client2, account_pairs):
        super().__init__()
        self.client1 = client1 # Client thread 1
        self.client2 = client2 # Client thread 
        self.account_pairs = account_pairs

    async def run(self):
        # Create datetime objects for 08:00 AM and 19:00 (7:00) PM #TODO: Check if this is UTC
        time1 = datetime.datetime.combine(datetime.date.today(), datetime.time(8))
        time2 = datetime.datetime.combine(datetime.date.today(), datetime.time(19))

        time1 = datetime.datetime.now()
        #time2 = time1

        now = datetime.datetime.now()
        future_time = (now + datetime.timedelta(seconds=1)).time()
        formatted_time = future_time.strftime("%H:%M:%S")

        # Schedule tasks to run at specific times
        # schedule.every().day.at(time.strftime("%H:%M", time1)).do(functools.partial(self.schedule_trades, self.account_pairs))
        schedule.every().day.at(formatted_time).do(functools.partial(self.schedule_trades, self.account_pairs))
        # schedule.every().day.at(time2.time().strftime("%H:%M")).do(self.close_hedged(account_pairs))

        # Schedule a task to run once every minute
        #schedule.every(1).minutes.do(None) #TODO: Check for closed trades to make sure the opposite trade also gets closed

        # Run the scheduler loop
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)  # Sleep to avoid high CPU usage

    def schedule_trades(self, account_pairs):
        pairs = tradeschedule.gen_trades(account_pairs)
        for acc_pair_time in pairs:
            acc_pair, delay = acc_pair_time
            threading.Timer(delay, functools.partial(self.open_hedged, acc_pair)).start()
    
    def open_hedged(self, acc_pair):
        acc1, acc2 = acc_pair
        # Use arbitrary/random decision to choose which account buys and which sells
        side_var = random.randint(0, 1)
        if side_var == 0:
            side_acc1 = "BUY"
            side_acc2 = "SELL"
        else:
            side_acc1 = "SELL"
            side_acc2 = "BUY"

        # Use the path that these account credentials are tied to
        # Check to make sure that the other account uses the other path
        if acc1[1]['path'] == acc2[1]['path']:
            print("Accounts %s and %s have same path. Exiting." % (acc1, acc2))
            quit();
        
        # Connect the accounts if not already connected
        if self.client1.account_name != acc1[0]: self.client1.connect(acc1[0], 1)
        if self.client2.account_name != acc2[0]: self.client2.connect(acc2[0], 2)
        
        # Place the trade through the thread mt5_client
        result1 = self.client1.open_pos(side_acc1)
        result2 = self.client2.open_pos(side_acc2)
        
        
        # TODO: Check success of opening positions (Fills, fails, need to retry, close opposite)
        


    #def run(self):
        # Implement central trading logic here
        #pass
        # Run trade schedule generator corroutine each day
        #asyncio.run(tradeschedule.main())
        
        
        
        # Is it up to the client threads to manage the trade schedules? Shouldn't be incase one gets hung up.
        # Central thread should take care of all trade scheduling and analyze success or failure of trade execution.
        # How are we going to handle closing positions for high volatility news events? How will we unify the time zones?




if __name__ == '__main__':
    # Create instances of account manager threads
    client_thread_1 = AccountManager()
    client_thread_2 = AccountManager()

    # Start the client threads
    client_thread_1.start()
    client_thread_2.start()

    account_pairs = accounts.create_account_pairs(filename)
    if account_pairs == 0:
        print("Account pairs failed to match.")
        quit()
    # Create an instance of the central thread and start it
    central_thread = CentralThread(client_thread_1, client_thread_2, account_pairs)
    asyncio.run(central_thread.run())
