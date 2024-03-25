# GmailAPI

This repository contains two scripts located in the `/scripts` folder and a utility folder for all utility functions and constants. These scripts are intended to be run on a server using cron jobs.

## 1. `fetch_and_push_emails.py`

This script connects to the Gmail API using the `google-api-python-client` library and fetches all emails associated with the specified user ID.

### Prerequisites:
- Setting up credentials in the Google Console. Refer to the [Google documentation](https://developers.google.com/gmail/api/quickstart/python) for instructions.
- Once the credentials file is created, upload it to AWS S3 for security reasons.
- The script also pushes data to a SQL database. Update the database credentials in the environment variables to fetch data from there.

### How to run the script:
1. Install the required dependencies.
2. Run the following command:
   ```bash
   python scripts/fetch_and_push_emails.py

## 2. `rule_applier.py`

This script will read all the emails from DB and filter the ones, for which rule is not applied yet. The script will then iterate over the emails and apply the rule if the conditions are satisfied.

### Prerequisites:
- I have pre-created the rules and added it as a json and added it in utils folder
### How to run the script:
1. Run the following command:
   ```bash
   python scripts/rule_applier.py
