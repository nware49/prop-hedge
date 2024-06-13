import datetime
import asyncio
import schedule
import random

trade_schedule = None

async def gen_trades(account_pairs):
    await asyncio.sleep(1) # What does this do?
    global trade_schedule
    # Pick random times. Uses precision to the second. 
    for pair in account_pairs:
        pair_name = pair["name"]
        num_trades = int(pair["num_day_trades"])
        open_time = datetime(pair["day_open"])
        close_time = datetime(pair["day_close"])
        # Generate a random float between 1 and 4
        random_hours = random.uniform(1, 4)
        # Create a timedelta object with the random number of hours
        random_timedelta = datetime.timedelta(hours=random_hours)
        first_trade = open_time + random_timedelta #TODO: Make sure open_time is a datetime object
        trade_times = [first_trade]
        for i in num_trades - 2: #TODO: Check that this for loop functions correct
            random_hours = random.uniform(4, 5)
            random_timedelta = datetime.timedelta(hours=random_hours)
            next_trade = trade_times[-1] + random_timedelta
            if next_trade < (close_time - datetime.timedelta(hours=5)):
                # There is sufficient time for the trade to play out
                trade_times.append(next_trade)

        trade_schedule[pair_name] = trade_times #TODO: Figure out if this global can be read by main when it is updated


async def close_trades(accounts):
    await asyncio.sleep(5) # What does this do? Is it necessary?
    # Use MT5 terminal and credentials list to log into all accounts and close any open trades.
    for acc in accounts:
        pass


async def main(accounts, account_pairs):
    # Create datetime objects for 01:00 AM and 19:00 (7:00) PM #TODO: Check if this is UTC
    time1 = datetime.datetime.combine(datetime.date.today(), datetime.time(1))
    time2 = datetime.datetime.combine(datetime.date.today(), datetime.time(19))

    # Schedule tasks to run at specific times
    schedule.every().day.at(time1.time().strftime("%H:%M")).do(gen_trades(account_pairs))
    schedule.every().day.at(time2.time().strftime("%H:%M")).do(close_trades(accounts))

    # Schedule a task to run once every minute
    schedule.every(1).minutes.do(None) #TODO: Check for closed trades to make sure the opposite trade also gets closed

    # Run the scheduler loop
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Sleep to avoid high CPU usage