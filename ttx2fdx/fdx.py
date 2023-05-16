import requests
import json

# Your Freshdesk domain and API Key
domain = 'godtnok'
api_key = 'SgsXN7XaNbf33DDWoBxT'
password = '(Volvo90V))'  # Replace with your password

credentials = (api_key, password)

# The Freshdesk API url to get companies
url = f'https://{domain}.freshdesk.com/api/v2/companies'

# Send a GET request to the Freshdesk API
response = requests.get(url, auth=credentials)

# If the response was successful, no Exception will be raised
response.raise_for_status()

# Get the JSON data from the response
data = response.json()

# Loop through each company
for company in data:
    # Get the value of the 'customerid' custom field
    customer_id = company['custom_fields'].get('customerid')
    
    # If 'customerid' exists and is not empty, print the company
    if customer_id:
        print(f"{customer_id} - {company['name']}")
