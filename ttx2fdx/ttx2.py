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
url_to_get_customer = URL #+ "/customer?customerNumber=100030"

response = requests.get(url_to_get_customer, headers=headers)

# If the response was successful, no Exception will be raised
response.raise_for_status()

# Call to retrieve customerNumber 100030
APIResponse2 = response.json()

pretty_json = json.dumps(APIResponse2, indent=4)
cusfile = "cus.txt"
with open(cusfile, "w") as c:
    c.write(pretty_json)
