import requests
import base64
import json
import datetime
import os
import pickle

# Tripletex PROD
URL = "https://tripletex.no/v2"
consumerToken = "eyJ0b2tlbklkIjo0NDQ0LCJ0b2tlbiI6ImM1MjQwODA3LTI1Y2UtNDhiMC04OGExLTI3YTUzYTYyN2M1ZCJ9"
employeeToken = "eyJ0b2tlbklkIjo3ODA4NTUsInRva2VuIjoiZWRlMTkzYjQtY2M0Yi00YjBmLTk3ZDItMjIxM2UxNzk3NGQ1In0="

# Session token Expiration date
expirationDate = "2023-12-31"

# File to store the sessionToken and expirationDate
token_file = "token.pkl"

# Check if the file exists and if the token is still valid
if os.path.exists(token_file):
    with open(token_file, "rb") as f:
        data = pickle.load(f)
        print(data)
    if data["expirationDate"] > datetime.datetime.now():
        sessionToken = data["sessionToken"]
        print(f"Using existing token, expiring on {data['expirationDate']}: {sessionToken}\n\n")
    else:
        # Generate a new token
        raise Exception("Token expired. Please generate a new one.")
else:
    # Generate a new token
    url_to_create_session = URL + "/token/session/:create?consumerToken=" + consumerToken + "&employeeToken=" + employeeToken + "&expirationDate=" + expirationDate
    response = requests.put(url_to_create_session, headers={"Content-Type": "application/json"})
    response.raise_for_status()
    APIResponse1 = response.json()
    sessionToken = APIResponse1['value']['token']

    # Save the token to a file
    with open(token_file, "wb") as f:
        pickle.dump({
            "sessionToken": sessionToken,
            "expirationDate": datetime.datetime.strptime(expirationDate, "%Y-%m-%d")
        }, f)
        print(f"Created new token, expiring on {expirationDate}: {sessionToken}")

# Encrypting '0:<sessionToken>' into encryptedToken 
encryptedToken = base64.b64encode(("0:" + sessionToken).encode('utf-8')).decode('utf-8')

# Set Basic authentication using the encrypted Session Token
headers = {
    'Authorization': "Basic " + encryptedToken,
    'Content-Type': 'application/json'
}

# API-parameters to retrieve record for customerNumber 100030
url_to_get_customer = URL + "/customer?customerNumber=100030"

response = requests.get(url_to_get_customer, headers=headers)

# If the response was successful, no Exception will be raised
response.raise_for_status()

# Call to retrieve customerNumber 100030
APIResponse2 = response.json()

pretty_json = json.dumps(APIResponse2, indent=4)
#print(pretty_json)

# Prepare the data for the new order
new_order = {
    "customer": {
        "customerNumber": 100001,
        "name": "Sola Strand Hotel"
    },
    "orderLines": [
        {
            "product": {"id": 1000},
            "description": "This is a test",
            "count": 1
        }
    ],
    "orderDate": datetime.datetime.now().isoformat(),
    "deliveryDate": datetime.datetime.now().isoformat()
}

# Convert the Python dictionary to a JSON string
new_order_json = json.dumps(new_order)

# Create the new order
order_endpoint = URL + "/order"
response = requests.post(order_endpoint, headers=headers, data=new_order_json)
print(f"HEADERS>> {response.headers}\n\n")
print(f"REASON>> {response.reason}\n\n")
print(f"TEXT {response.text}\n\n")

# Raise an exception if the request was unsuccessful
response.raise_for_status()

# Print the response from the API
print("New order created:", response.json())
