import requests
import json

# Define the API endpoint and authentication token
api_url = 'https://api.dxtrade.com/v1/trade'
auth_token = 'your_auth_token_here'

# Define the trade parameters
trade_params = {
    'symbol': 'EURUSD',
    'action': 'buy',
    'volume': 0.1,
    'price': 1.2000,
    'sl': 1.1950,
    'tp': 1.2100,
    'comment': 'Buy EURUSD at 1.2000 with SL at 1.1950 and TP at 1.2100'
}

# Create the headers with authentication token
headers = {
    'Authorization': f'Bearer {auth_token}',
    'Content-Type': 'application/json'
}

# Make the POST request
response = requests.post(api_url, headers=headers, data=json.dumps(trade_params))

# Check the response
if response.status_code == 200:
    print('Trade executed successfully.')
    print(response.json())  # Optionally, print the response data
else:
    print('Error executing trade:')
    print(response.status_code, response.text)