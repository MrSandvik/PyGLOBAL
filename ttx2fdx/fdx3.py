import requests
import json
from datetime import datetime

# Your Freshdesk domain and API Key
domain = 'godtnok'
api_key = 'SgsXN7XaNbf33DDWoBxT'
password = '(Volvo90V))'  # Replace with your password

credentials = (api_key, password)

# Function to convert hh:mm to decimal
def time_to_decimal(time):
    hours, minutes = map(int, time.split(':'))
    return hours + minutes / 60.0

# URL definitions
time_url = f'https://{domain}.freshdesk.com/api/v2/time_entries?billable=true'
ticket_url = f'https://{domain}.freshdesk.com/api/v2/tickets'
company_url = f'https://{domain}.freshdesk.com/api/v2/companies'

# Calling the Freshdesk API to get all companies
company_response = requests.get(company_url, auth=credentials)
company_response.raise_for_status()
company_data = {company['id']: company for company in company_response.json()}  # convert list to dictionary
with open('companies.json', 'w') as f:
    json.dump(company_response.json(), f)

# Calling the Freshdesk API to get unbilled time entries
time_response = requests.get(time_url, auth=credentials)
time_response.raise_for_status()
time_data = time_response.json()

# Loop through each time entry
for time_entry in time_data:
    ticket_id = time_entry['ticket_id']
    time_duration = time_to_decimal(time_entry['time_spent'])
    time_raw = time_entry['start_time']
    time_object = datetime.strptime(time_raw, "%Y-%m-%dT%H:%M:%SZ")
    time_date = time_object.strftime("%Y-%m-%d")
    
    ticket_response = requests.get(f"{ticket_url}/{ticket_id}?include=requester,company", auth=credentials)
    ticket_response.raise_for_status()
    ticket_data = ticket_response.json()
    ticket_description = ticket_data['subject']
    ticket_contact = ticket_data['requester']['name']
    company_id = ticket_data['company']['id']
    company_details = company_data.get(company_id, {})  # get company details from dictionary
    company_name = company_details.get('name', 'N/A')
    custom_fields = company_details.get('custom_fields', {})
    company_no = custom_fields.get('customerid', 'N/A')
    

    print(f"#{ticket_id}, {ticket_contact}, {ticket_description}, {time_date}: {time_duration}, Company: {company_name}, {company_no}, {company_id}")
