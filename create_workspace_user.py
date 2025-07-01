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

def delete_user(email):
    try:
        creds = load_credentials()
        service = build("admin", "directory_v1", credentials=creds)
        service.users().delete(userKey=email).execute()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def delete_all_users(domain):
    try:
        creds = load_credentials()
        service = build("admin", "directory_v1", credentials=creds)
        users = service.users().list(domain=domain, maxResults=500, orderBy='email').execute().get('users', [])
        for user in users:
            email = user['primaryEmail']
            try:
                service.users().delete(userKey=email).execute()
            except Exception as e:
                print(f"Error deleting user {email}: {e}")
        return True
    except Exception as e:
        print(f"Error deleting all users: {e}")
        return False
