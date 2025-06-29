import os.path
import json
import random
import string
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required to manage users
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

# Load or generate credentials
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Random secure-ish password
def generate_password(length=10):
    password=''.join(random.choices(string.ascii_letters + string.digits, k=length))
    print(f"Generated password: {password}")  # Debugging output
    return password

def main():
    creds = get_credentials()
    service = build('admin', 'directory_v1', credentials=creds)

    user = {
        "primaryEmail": "test@yourdomain",  # change domain
        "name": {
            "givenName": "Test",
            "familyName": "User"
        },
        "password": generate_password(),
        "changePasswordAtNextLogin": True
    }

    try:
        result = service.users().insert(body=user).execute()
        print(f"✅ User created: {result['primaryEmail']}")
        print(f"✅ token created")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
