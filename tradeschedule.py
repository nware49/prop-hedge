import datetime
import asyncio
import schedule
import tradealgo


def gen_trades(account_pairs):
    account_trade_times = algo_trades(account_pairs)
    return account_trade_times


def close_trades(accounts):
    # await asyncio.sleep(5) # What does this do? Is it necessary?
    # Use MT5 terminal and credentials list to log into all accounts and close any open trades.
    for acc in accounts:
        pass
