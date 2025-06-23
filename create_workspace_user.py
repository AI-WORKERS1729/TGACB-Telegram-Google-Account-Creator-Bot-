import json
import random
import string
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_credentials():
    return Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/admin.directory.user"])

def random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_user(info):
    try:
        creds = load_credentials()
        service = build("admin", "directory_v1", credentials=creds)

        password = random_password()
        user_body = {
            "primaryEmail": info["primaryEmail"],
            "name": {
                "givenName": info["givenName"],
                "familyName": info["familyName"]
            },
            "password": password,
        }

        if info.get("recoveryEmail"):
            user_body["recoveryEmail"] = info["recoveryEmail"]
        if info.get("recoveryPhone"):
            user_body["recoveryPhone"] = info["recoveryPhone"]
        if info.get("orgUnitPath"):
            user_body["orgUnitPath"] = info["orgUnitPath"]

        service.users().insert(body=user_body).execute()
        return password
    except Exception as e:
        print(f"Error: {e}")
        return None

def set_token_content(token_str):
    with open("token.json", "w") as f:
        f.write(token_str)

def user_exists(email):
    try:
        creds = load_credentials()
        service = build("admin", "directory_v1", credentials=creds)
        service.users().get(userKey=email).execute()
        return True
    except Exception as e:
        if "Resource Not Found" in str(e) or "notFound" in str(e):
            return False
        return None