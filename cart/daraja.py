      
import requests
import datetime
import base64
from decouple import config



class MpesaClient():
   
    def __init__(self):
        self.headers =None
        self.passkey = config("passkey")
        self.business_short_code = "174379"
        self.timestamp = None
        self.access_token = None  # Instance variable to store timestamp
        
    def generate_password(self):
        now = datetime.datetime.now()
        self.timestamp = now.strftime("%Y%m%d%H%M%S")  # Store the generated timestamp
        concatenated_string = self.business_short_code + self.passkey + self.timestamp
        encoded_password = base64.b64encode(concatenated_string.encode("utf-8")).decode("utf-8")
        return encoded_password


    def accessToken(self):
        authorization ="MlZ4M3JQcjdoYk52dnh5ckFSR1JaUmlWd3R0U3lERVo6MnVyN3hYeWNDZDhra3BWZQ=="
        heders ={
        'Authorization': f'Basic {authorization}'
        }
        response = requests.get('https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials', headers=heders)   
        json_response = response.json()
        self.access_token = json_response["access_token"]
        print(self.access_token)
        return response

    
    def make_stk_push(self, amount, phone_number, callback_url, account_reference, transaction_desc):
        self.accessToken()
        password = self.generate_password()
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        print(self.headers)
        
        payload = {
            "BusinessShortCode": self.business_short_code,
            "Password": password,
            "Timestamp": self.timestamp,  # Use the stored timestamp
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }

        response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers=self.headers, json=payload)

        decoded_response = response.text.encode('utf8').decode()
        json_response = response.json()
        print(json_response)
        return json_response

    
    
# call=MpesaClient()
# # call.accessToken()
# call.make_stk_push(5, "254798391330","https://mydomain.com/path","CompanyXLTD","Payment of X")