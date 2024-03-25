import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.sql_connector import fetch_emails, update_email
from utils.rules import RULES as rule_json
from fetch_and_push_emails import GmailAPI
from datetime import datetime, timedelta, timezone

user_id = "me"
gmail_api = GmailAPI()


def parse_date(date_string):
    """
    Parse a date string into a datetime object.

    Args:
        date_string (str): The date string to parse.

    Returns:
        datetime.datetime: A datetime object representing the parsed date and time.
    """
    date_format = "%a, %d %b %Y %H:%M:%S %z (%Z)"
    return datetime.strptime(date_string, date_format)


def apply_condition(condition, email):
    """
    Apply a condition to an email.

    Args:
        condition (dict): A dictionary representing the condition to apply.
        email (tuple): A tuple representing the email containing subject, from_address, to_address, and date.

    Returns:
        bool: True if the condition is satisfied, False otherwise.
    """
    field = condition.get("field")
    value = condition.get("value")

    if field == "from_address":
        return value in email[1]
    elif field == "subject":
        return value in email[0]
    elif field == "date":
        date_received = parse_date(email[3])
        current_datetime = datetime.now().astimezone(tz=timezone.utc)
        difference = current_datetime - date_received
        if difference < timedelta(days=2):
            return True
        else:
            return False
    return False


def is_condition_satisfied(rule, email):
    """
    Check if a rule's conditions are satisfied for an email.

    Args:
        rule (dict): A dictionary representing the rule to check.
        email (tuple): A tuple representing the email containing subject, from_address, to_address, and date.

    Returns:
        bool: True if all conditions are satisfied, False otherwise.
    """
    if rule["type"] == "all":
        is_conditions_met = all(
            apply_condition(condition, email)
            for condition in rule.get("conditions", [])
        )
    return is_conditions_met


def apply_action(rule, email):
    """
    Apply actions specified in a rule to an email.

    Args:
        rule (dict): A dictionary representing the rule containing actions to apply.
        email (tuple): A tuple representing the email containing subject, from_address, to_address, and date.

    Returns:
        None
    """
    action_applied = False
    for action in rule.get("actions", []):
        action_type = action.get("action")
        if action_type == "move_to_mailbox":
            gmail_api.move_to_inbox(user_id, email[4])
            action_applied = True
        elif action_type == "mark_as_read":
            gmail_api.mark_as_read(user_id, email[4])
            print(f"Marking email '{email[1]}' as read")
            action_applied = True
    if action_applied:
        update_email(email[4])


def main():
    """
    Main function to fetch emails, apply rules, and take actions.

    Returns:
        None
    """
    emails = fetch_emails()
    for email in emails:
        rule = rule_json["rules"][0]
        is_condition_met = is_condition_satisfied(rule, email)
        if is_condition_met:
            apply_action(rule, email)


if __name__ == "__main__":
    main()
