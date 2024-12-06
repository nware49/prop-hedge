# Proprietary Firm Hedging Algorithm

## Project Status

# Improvements

- [ ] Position sizing is not robust
- [x] Position management needed
- [ ] Close partials with limit orders (not possible?)
- [x] Move Stop Loss (SL) to Break Even (BE)
- [ ] Better message handling
- [x] Average down

## Layered Alert Handling
- [x] Parse Discord alert
- [x] Generate order object
- [x] Send order object to MT5 client
- [x] Place order
- [x] Use order comment to distinguish between alerters
  - This way, you don't have to keep a dictionary of open positions

## Order Object Attributes
- [x] Can't use MT5 attributes
- [x] Set attribute defaults

**Note:** Move SL to BE and trim a little after the alerter takes the first trim.

# Tuning

- [x] Tune position sizing
  - 5% of account?
  - Risk-based vs. Position size-based
- [ ] Tune SL/TP for each alerter
- [ ] Weed out meaningless messages
- [ ] Add more alert handlers: Donvo? $125 per month
- [ ] Problems with Donvo: Blueberry broker means entries, SL, and TP will be different
- [ ] Fix xTrades alert parsing

## Drawdown Protector
- [x] Calculate profit (`Calc_profit`)
- [x] Open positions * SL = max drawdown
- [x] Calculate if a new trade can be opened by subtracting drawdown from the account balance
- [ ] Does UTC date correspond to drawdown date change?
- [ ] **ISSUE:** Doesn't seem to be working - hopefully fixed

## Other Tuning
- [ ] Disable/Enable autotrading - can't do this
- [x] Close open positions if a new trade is opened
- [x] If `@deleted-role` in message, pop from message/ignore in parsing
- [x] Fix delete pending

- [x] Log position opening in Discord - map to messages
- [x] Uptime for message mirror
- [x] Uptime for MT5 terminal

# Installation

- [ ] Use services that run on startup
- [x] Uptime bot for selfbot mirror
- [x] Uptime bot with Slack messages
- [x] Add error handling to message forwarder
- [ ] Cost management on servers

# Future

- [ ] Alerter evaluation with imaginary money
  - Get data and track entries/exits instead of executing trades on MT5 demo
  - Multiple accounts for real entries and exits
- [ ] MT5 Expert Advisor
- [ ] Copy Trading between MT4 and MT5 accounts for multiple prop firms
- [ ] Implement on options brokerages
- [ ] Move away from Virtual Workspace
  - Expert advisor seems to require a running MT5 terminal
- [ ] Multiple accounts
