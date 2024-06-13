import threading
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import client
import accounts
import tradeschedule
import asyncio
import datetime

# Create a class for handling accounts on DXTrade and TradeLocker
class AccountManager(threading.Thread):
    def __init__(self):
        super().__init__()
        # One single MT5 connection should be established for each thread and used by all MT5 accounts
        self.mt5_client = None
        return self
    
    # Refactor to initialize a MT5 connection on both threads on startup
    # Then connect to platform each time you want to place a trade
    # No real urgency, don't need to worry about time spent logging in
    # 
    
    def run(self):
        pass
    
    def connect(self, account_name):
        # Get account
        self.account = accounts.fetch_account_data(account_name)
        # Determine which platform to connect to
        platform = self.account['platform']
        # TODO: Condense to lookup table?
        if platform == "MT5": # Connect to MT5 client manager
            self.client = accounts.connect_MT5(self.mt5_client, self.account)
            if self.mt5_client == None: self.mt5_client = self.client #TODO: Fix this.
        elif platform == "DXTrade": # Connect to DXTrade with ____ request
            self.client = 0
        elif platform == "TradeLocker": # TODO: Not sure how to connect yet
            self.client = 0
        else: # Unsupported platform, return failed connection
            self.client = 0
        
        if self.client == 0: return 0 # Failed to connect to platform, return
        return self
    
    def trade(self):
        if platform == "MT5"
        pass


class CentralThread(threading.Thread):
    def __init__(self, client1, client2):
        super().__init__()
        self.client1 = client1 # Client thread 1
        self.client2 = client2 # Client thread 2


    def run(self):
        # Implement central trading logic here
        pass
        # Run trade schedule generator corroutine each day
        asyncio.run(tradeschedule.main())
        # Is it up to the client threads to manage the trade schedules? Shouldn't be incase one gets hung up.
        # Central thread should take care of all trade scheduling and analyze success or failure of trade execution.




if __name__ == '__main__':
    # Create instances of account manager threads
    client_thread_1 = AccountManager()
    client_thread_2 = AccountManager()

    # Start the client threads
    client_thread_1.start()
    client_thread_2.start()

    # Create an instance of the central thread and start it
    central_thread = CentralThread(client_thread_1, client_thread_2)
    central_thread.start()
