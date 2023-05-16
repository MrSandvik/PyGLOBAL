import argparse
import pickle
import os
import requests
import getpass
import json
import base64

def get_credentials():
    # Check if credentials file exists
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as f:
            credentials = pickle.load(f)
    else:
        credentials = {}

        # Tripletex credentials
        print("Enter your Tripletex credentials:")
        credentials['ttx'] = {}
        credentials['ttx']['url'] = input("Enter API base URL (default: https://tripletex.no/v2): ") or "https://tripletex.no/v2"
        credentials['ttx']['consumerToken'] = input("Enter Consumer Token: ")
        credentials['ttx']['employeeToken'] = input("Enter Employee Token: ")
        credentials['ttx']['expirationDate'] = input("Enter expiration date (default: 2099-12-31): ") or "2099-12-31"

        # Generate Tripletex session token
        url_to_create_session = credentials['ttx']['url'] + "/token/session/:create?consumerToken=" + credentials['ttx']['consumerToken'] + "&employeeToken=" + credentials['ttx']['employeeToken'] + "&expirationDate=" + credentials['ttx']['expirationDate']
        print(f"url: {url_to_create_session}\n\n\n")
        response = requests.put(url_to_create_session, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        APIResponse1 = response.json()
        credentials['ttx']['sessionToken'] = APIResponse1['value']['token']

        # Freshdesk credentials
        print("\nEnter your Freshdesk credentials:")
        credentials['fdx'] = {}
        credentials['fdx']['url'] = input("Enter API base URL (i.e. domain prefix for <domain>.freshdesk.com): ") + ".freshdesk.com"
        credentials['fdx']['apiKey'] = input("Enter API Key: ")
        credentials['fdx']['password'] = getpass.getpass("Enter Password: ")

        # Save credentials to file
        with open('token.pkl', 'wb') as f:
            pickle.dump(credentials, f)

    return credentials

def testAPI(api, credentials):
    
    if api == "ttx":
        with open('log.txt', 'w') as f:
            # Encrypting '0:<sessionToken>' into encryptedToken 
            encryptedToken = base64.b64encode(("0:" + credentials['ttx']['sessionToken']).encode('utf-8')).decode('utf-8')

            # Set Basic authentication using the encrypted Session Token
            headers = {
                'Authorization': "Basic " + encryptedToken,
                'Content-Type': 'application/json'
            }

            # API-parameters to retrieve record for customerNumber 100030
            url_to_get_customer = credentials['ttx']['url'] + "/customer?customerAccountNumber=100030"

            response = requests.get(url_to_get_customer, headers=headers)
            
            # If the response was successful, no Exception will be raised
            response.raise_for_status()

            # Call to retrieve customerNumber 100030
            APIResponse2 = response.json()
            
            pretty_json = json.dumps(APIResponse2, indent=4)
            
            f.write("Tripletex>>\n")
            f.write(pretty_json)
            f.write("\n\n")

    elif api == "fdx":
        with open('log.txt', 'a') as f:
            domain = credentials['fdx']['url'].split(".")[0]  # Split the URL to get the domain
            api_key = credentials['fdx']['apiKey']
            password = credentials['fdx']['password']

            credentials = (api_key, password)

            # The Freshdesk API url to get tickets
            url = f'https://{domain}.freshdesk.com/api/v2/tickets'

            # Send a GET request to the Freshdesk API
            response = requests.get(url, auth=credentials)

            # If the response was successful, no Exception will be raised
            response.raise_for_status()

            # Get the JSON data from the response
            data = response.json()

            # Get the most recent ticket
            most_recent_ticket = data[0]  # Assuming tickets are ordered by most recent

            # Print the details of the most recent ticket
            f.write(json.dumps(most_recent_ticket, indent=4))

def main():
    parser = argparse.ArgumentParser(description='Process API tasks.')
    parser.add_argument('--startDate', type=str, help='Start date in the format YYYY-MM-DD')
    parser.add_argument('--endDate', type=str, help='End date in the format YYYY-MM-DD')
    parser.add_argument('--transfer', action='store_true', help='Transfer data')

    args = parser.parse_args()

    credentials = get_credentials()

    print(credentials)  # print to see if credentials are loaded correctly

    # Test both APIs
    testAPI("ttx", credentials)
    testAPI("fdx", credentials)

if __name__ == "__main__":
    main()