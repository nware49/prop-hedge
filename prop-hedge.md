`prop-hedge.txt`

``Overarching Plan``
Create a Python trading algorithm that can manage multiple MT5 terminals with the MetaTrader5 Python API. 

``Goals``
- Credential Manager
- Hedging Positions Between 2 Accounts
- Account Switching
- Stop Loss Management
- Prop Requirement Adaptability
- Acknowledge Daily Loss Requirements and Overnight/Weekend Trading

``Requirements``
- Log into two different MT5 terminals at once
- Place two trades at the same time
- When a trade is placed on one account, place an opposite trade on another account
- Log into new accounts with algorithmic trading enabled
- Place the sets of trades at slightly different times in the day to reduce risk of slippage violating daily drawdown
- Use a margin of safety to prevent violating daily drawdown rules
- Close trades before the end of the day to avoid violating rules
- Close trades when the profit target has been met
- Manually input the prop firm specifications
- Needs to be light enough to run consistently on the Windows virtual private machine

``Structure``
- Two instances of the MT5 client thread
- Central thread to dispatch trades
- Functions to manage active prop firm accounts and associated details
- Thread to create trades based on prop firm account requirements and details

``Messaging Alerts``
- Set up new Slack channel
- Create more informative messaging schema including the account number/broker
- Text message alerts if necessary
- Use text message to restart algo incase broken
- Reset needs to account for currently open or daily drawdown, otherwise daily drawdown could be exceeded
- Configure new accounts through messages

``Infrastructure``
- Is more RAM needed for the Workspace to run this without crashing
- Can a cheaper Linux workspace be used
- Will the script be able to switch between accounts enough to manage all trading accounts

``Main Script``
- Get pair of accounts from list
- Pass each account to a MT5 client
- Name MT5 clients based on the terminal application, not the direction of the trades they take
- Get most recent trade history from the accounts
- Perscribe trades to the two accounts based on last trade type and time
- Wait some time and move on to the next set of accounts

``Prop Firms``
- Vet prop firms
- Figure out which platform will be used
- Find best deals and most relaiable prop firms
- Allow EA trading