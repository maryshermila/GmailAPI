import os
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.sql_connector import insert_email
import boto3


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]
bucket_name = "my-bucket"
user_id = "me"
s3 = boto3.client("s3")


class GmailAPI:
    def __init__(self):
        self.creds = self._authenticate()
        self.service = build("gmail", "v1", credentials=self.creds)

    def _authenticate(self):
        """
        Authenticate with the Gmail API.

        This method authenticates with the Gmail API using OAuth 2.0.
        It reads token and credentials files from an S3 bucket.

        Args:
            bucket_name (str): Name of the S3 bucket containing token and credentials files.

        Returns:
            google.oauth2.credentials.Credentials: Authenticated credentials object.
        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                object_key = "google-api/credentials.json"
                credentials_file = self._read_file_from_s3(
                    bucket_name=bucket_name,
                    object_key=object_key,
                    output_file="credentials.json",
                )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def _read_file_from_s3(self, bucket_name, object_key, output_file):
        """
        Read a file from an S3 bucket.

        This method reads a file from an S3 bucket and writes its content to a local file.

        Args:
            bucket_name (str): Name of the S3 bucket.
            object_key (str): Key of the object in the S3 bucket.
            output_file (str): Name of the local file to write the content to.

        Returns:
            str: Content of the file.
        """
        try:
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            content = response["Body"].read().decode("utf-8")

            with open(output_file, "wb") as f:
                f.write(content)
            print("Content of the file:")
            print(content)
            return content
        except Exception as e:
            print(f"Error reading file from S3: {e}")
            return None

    def read_emails(self):
        """
        Read emails from the user's inbox.

        This method fetches emails from the user's inbox using the Gmail API.
        It iterates over fetched emails, extracts relevant information, and
        inserts them into a database.

        Args:
            user_id (str): User ID of the Gmail account.

        Returns:
            list: List of email objects.
        """
        results = (
            self.service.users()
            .messages()
            .list(userId=user_id, labelIds=["INBOX"])
            .execute()
        )
        messages = results.get("messages", [])
        email_list = []
        if not messages:
            print("No messages found.")
        else:
            print("Messages Found:")
            # Iterate over the messages and filter only the necessary values
            for message in messages:
                msg = (
                    self.service.users()
                    .messages()
                    .get(userId=user_id, id=message["id"])
                    .execute()
                )
                headers = msg["payload"]["headers"]
                for item in headers:
                    if item["name"] == "Subject":
                        subject = item["value"]
                    if item["name"] == "From":
                        from_address = item["value"]
                    if item["name"] == "To":
                        to_address = item["value"]
                    if item["name"] == "Date":
                        date = item["value"]
                    unique_id = message["id"]

                insert_email(
                    subject=subject,
                    from_address=from_address,
                    to_address=to_address,
                    date=date,
                    unique_id=unique_id,
                )

        return email_list

    def move_to_inbox(self, user_id, message_id):
        """
        Move an email to the inbox.

        This method moves an email to the inbox by removing specific label IDs.

        Args:
            user_id (str): User ID of the Gmail account.
            message_id (str): ID of the email message.

        Returns:
            None
        """
        try:
            self.service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={
                    "removeLabelIds": [
                        "UNREAD",
                        "CATEGORY_SOCIAL",
                        "CATEGORY_PROMOTIONS",
                        "CATEGORY_UPDATES",
                        "CATEGORY_FORUMS",
                    ]
                },
            ).execute()
            print("Email moved to 'Inbox' successfully.")
        except Exception as e:
            print(f"Error moving email to 'Inbox': {e}")

    def mark_as_read(self, user_id, message_id):
        """
        Mark an email as read.

        This method marks an email as read by removing the "UNREAD" label.

        Args:
            user_id (str): User ID of the Gmail account.
            message_id (str): ID of the email message.

        Returns:
            None
        """
        try:
            self.service.users().messages().modify(
                userId=user_id, id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            print("Email marked as read successfully.")
        except Exception as e:
            print(f"Error marking email as read: {e}")


if __name__ == "__main__":
    gmail_api = GmailAPI()
    gmail_api.read_emails()
