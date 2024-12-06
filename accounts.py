import json
from client import mt5_client

def fetch_account_data(filename, acc_nickname=None):
    # Read file containing account data
    with open(filename, 'r') as file:
        data = json.load(file)
    if acc_nickname == None:
        account_data = data
    else: # Return dictionary with account details or an empty dictionary if nickname doesn't exist
        account_data = data.get(acc_nickname, {})
    
    return account_data

def create_account_pairs(filename):
    acc_data = fetch_account_data(filename)
    pairs = []
    accounts = list(acc_data.items())
    for i in range(0, len(accounts), 2):
        first_acc = accounts[i]
        second_acc = accounts[i + 1] if i + 1 < len(accounts) else None
        if second_acc == None: return
        # if (first_acc["hedge_to"] != second_acc) or (second_acc["hedge_to"] != first_acc): 
        #     print("Account 'hedge to' names do not match. Pair", i)
        #     return 0
        # if (first_acc['us_traders'].upper()!="TRUE") or (first_acc['ea_allowed'].upper()!="TRUE"):
        #     print("First account not allowed US or EA. Pair", i)
        #     return 0
        # if (second_acc['us_traders'].upper()!="TRUE") or (second_acc['ea_allowed'].upper()!="TRUE"):
        #     print("Second account not allowed US or EA. Pair", i)
        #     return 0
        #TODO: DONE? Give pair attributes, check and improve above logic
        pair = (first_acc, second_acc)
        pairs.append(pair)

    return pairs

def get_data(mt5_conn):
    pair = "XAUUSD"
    symbol_info = mt5_conn.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return
        

def connect_MT5(account, version):
    # Create a connection to the MT5 terminal which can be utilized by the account manager thread if it does not already exist
    mt5_connection = mt5_client(account, version)

    #mt5_connection.get_data()

    # Check if connection is authorized
    if mt5_connection.authorized == False:
        quit(code="MT5 account unauthorized.")
    
    return mt5_connection