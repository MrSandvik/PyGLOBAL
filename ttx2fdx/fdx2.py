import requests
import json

# Your Freshdesk domain and API Key
domain = 'godtnok'
api_key = 'SgsXN7XaNbf33DDWoBxT'
password = '(Volvo90V))'  # Replace with your password

credentials = (api_key, password)

# Function to convert hh:mm to decimal
def time_to_decimal(time):
    hours, minutes = map(int, time.split(':'))
    return hours + minutes / 60.0

# The Freshdesk API url to get companies
companies_url = f'https://{domain}.freshdesk.com/api/v2/companies'
companies_response = requests.get(companies_url, auth=credentials)
companies_response.raise_for_status()
companies_data = companies_response.json()

# Loop through each company
for company in companies_data:
    customer_id = company['custom_fields'].get('customerid')
    if customer_id:
        print(f"Customer: {customer_id} - {company['name']}")
        
        # Get tickets for this company
        tickets_url = f"https://{domain}.freshdesk.com/api/v2/tickets?company_id={company['id']}&include=requester"
        tickets_response = requests.get(tickets_url, auth=credentials)
        tickets_response.raise_for_status()
        tickets_data = tickets_response.json()
        
        # Loop through each ticket
        for ticket in tickets_data:
            # Get time entries for this ticket
            time_entries_url = f"https://{domain}.freshdesk.com/api/v2/tickets/{ticket['id']}/time_entries"
            time_entries_response = requests.get(time_entries_url, auth=credentials)
            time_entries_response.raise_for_status()
            time_entries_data = time_entries_response.json()

            # Loop through each time entry
            for time_entry in time_entries_data:
                if time_entry['billable']:
                    time_decimal = time_to_decimal(time_entry['time_spent'])
                    print(f"Ticket: #{ticket['id']}: ({ticket['requester']['name']}) {ticket['subject']} -- {time_decimal:.2f}")
