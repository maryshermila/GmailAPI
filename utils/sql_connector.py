import mysql.connector
import os


conn = mysql.connector.connect(
    host=os.environ.get("db_host"),
    user=os.environ.get("db_user"),
    password=os.environ.get("db_password"),
    database=os.environ.get("db_name"),
)
cursor = conn.cursor()


def check_table():
    """
    Create the 'emails' table if it doesn't exist.

    This function executes a SQL command to create the 'emails' table if it doesn't exist.
    The table schema includes columns for subject, from_address, to_address, date, unique_id, and actions_applied.

    Returns:
        None
    """
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
        subject TEXT NOT NULL,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        date TEXT NOT NULL,
        unique_id VARCHAR(255) NOT NULL PRIMARY KEY,
        actions_applied BOOLEAN NOT NULL DEFAULT FALSE
    )
    """
    )
    conn.commit()


def insert_email(subject, from_address, to_address, date, unique_id):
    """
    Insert an email into the 'emails' table.

    This function inserts an email into the 'emails' table with the provided details.
    If an email with the same unique_id already exists, it is ignored.

    Args:
        subject (str): The subject of the email.
        from_address (str): The sender's email address.
        to_address (str): The recipient's email address.
        date (str): The date the email was sent.
        unique_id (str): The unique identifier for the email.

    Returns:
        None
    """
    check_table()
    cursor.execute(
        "INSERT IGNORE INTO emails (subject, from_address, to_address, date, unique_id) VALUES (%s, %s, %s, %s, %s)",
        (subject, from_address, to_address, date, unique_id),
    )
    conn.commit()


def fetch_emails():
    """
    Fetch emails that have not had actions applied.

    This function executes a SQL query to fetch emails from the 'emails' table
    where actions_applied is FALSE (indicating actions have not been applied).

    Returns:
        list: A list of tuples containing the fetched emails.
    """
    try:
        cursor.execute("SELECT * FROM emails WHERE actions_applied = FALSE")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching emails from MySQL: {e}")
        return []


def update_email(unique_id):
    """
    Update the 'actions_applied' column for a specific email.

    This function executes an SQL UPDATE query to set actions_applied to TRUE
    for the email with the given unique_id.

    Args:
        unique_id (str): The unique identifier for the email to update.

    Returns:
        None
    """
    try:
        update_query = """
        UPDATE emails
        SET actions_applied = TRUE
        WHERE unique_id = %s
        """
        cursor.execute(update_query, (unique_id,))
        conn.commit()
    except Exception as e:
        print(f"Error in updating the email: {e}")
