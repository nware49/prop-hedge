import json
import client

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
    pairs = {}
    accounts = list(acc_data.item())
    for i in range(0, len(accounts), 2):
        pair = {}
        first_acc = accounts[i]
        second_acc = accounts[i + 1] if i + 1 < len(accounts) else None
        if second_acc == None: return
        if first_acc["hedge_to"] != second_acc["nickname"]: return
        if second_acc["hedge_to"] != first_acc["nickname"]: return
        else: pair_name = first_acc["nickname"]
        #TODO: Give pair attributes, check and improve above logic
        pairs[pair_name] = pair

    return pairs
        

def connect_MT5(mt5_connection, account):
    # Create a connection to the MT5 terminal which can be utilized by the account manager thread if it does not already exist
    if mt5_connection == None:
        mt5_connection = client.mt5_client(account['path'])
    # Connect the terminal to the account to be traded
    mt5_account = mt5_connection.connect(account)
    # Check if connection is authorized
    if mt5_account.authorized == False: return 0
    
    return mt5_account