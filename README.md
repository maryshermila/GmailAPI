# GmailAPI
The Repository has 2 scripts in /scripts folder and a utility folder for all the utility functions and constants
(Assuming the scripts will be running in a server using cron job)

1. fetch_and_push_emails.py
This script will connect with the GmailAPI through google-api-python-client and fetch all the emails that are associated with the user_id
Prerequistis:
    - This would require setting up things in google console.I have referred the google documentation to setup the same. Doc reference : https://developers.google.com/gmail/api/quickstart/python
    - Once the credentials file is created (from the above step) and I have uploaded it to aws s3 and reading it from there (for security reasons)
    - The script also pushes data to SQL - I have used my local SQL setup and updated the db creds in the env to fetch it from there 
Run the file:
    Install the requirements
    python scripts/fetch_and_push_emails.py

2. rule_applier.py
This script will read all the emails from DB and filter the ones, for which rule is not applied yet. The script will then iterate over the emails and apply the rule if the conditions are satisfied.
Prerequistis:
    - I have pre-created the rules and added it as a json and added it in utils folder
Run the file:
    python scripts/rule_applier.py


