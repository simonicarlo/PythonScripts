import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.header import decode_header
import sqlite3
import os
from dotenv import load_dotenv
import random
import logging

# Email and IMAP Configuration
load_dotenv()

# Mode of Operation
# 0: Development Mode - CLI for testing (no email sending)
# 1: Manual Mode - CLI for processing emails
# 2: Automated Mode - Process new emails and send automated replies (setup in cron job)

MODE = 0
MODE_DESCRIPTION = {0: "Development", 1: "Manual", 2: "Automated"}
current_mode = MODE_DESCRIPTION.get(MODE, "Unknown")

# Last UID Configuration
UID_FILE = "last_uid.txt"

# Logging Configuration
LOG_FILE = "history.log"
ENABLE_LOGGING = True

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [Mode: %(mode)s] - %(message)s",
)

# Automated Reply Configuration
AUTOREPLY_FILE = "autoreply1.txt"
AUTOREPLY_SUBJECT = "Danke für deine Email!"

# Email Configuration
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")


# Database Configuration
# SQLite setup for storing emails
conn = sqlite3.connect('emails.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS emails (email TEXT UNIQUE)")


# Logging
def log_info(message):
    print(message)
    if ENABLE_LOGGING:
        logging.info(message, extra={'mode': current_mode})

def log_error(message):
    print(f'ERROR: {message}')
    if ENABLE_LOGGING:
        logging.info(message, extra={'mode': current_mode})

# Function to get last UID
def get_last_uid():
    if os.path.exists(UID_FILE):
        with open(UID_FILE, 'r') as file:
            return file.read().strip()
    return None

# Function to save last UID
def save_last_uid(uid):
    with open(UID_FILE, 'w') as file:
        file.write(uid)
    log_info(f"Last UID saved as {uid}")

# Send automated reply
def send_automated_reply(sender_email):

    if not os.path.exists(AUTOREPLY_FILE):
        log_error(f"Automated reply file {AUTOREPLY_FILE} not found.")
        return

    with smtplib.SMTP(SMTP_SERVER, 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, PASSWORD)

        # Create a reply message from a file
        with open(AUTOREPLY_FILE, "r") as file:
            reply_message = file.read()

        msg = MIMEText(reply_message)
        msg["Subject"] = AUTOREPLY_SUBJECT
        msg["From"] = EMAIL
        msg["To"] = sender_email

        if MODE == 0:
            print(f"Development Mode: Sending {msg} to {sender_email}")
        else: 
            smtp.sendmail(EMAIL, sender_email, msg.as_string())
    log_info(f"Sent automated reply to {sender_email}")


# View stored emails
def view_stored_emails():
    cursor.execute("SELECT email FROM emails")
    all_emails = [row[0] for row in cursor.fetchall()]
    
    print("Stored Emails:")
    for idx, email in enumerate(all_emails):
        print(f"{idx}: {email}")

    return all_emails

def delete_email():
    # Fetch stored emails
    all_emails = view_stored_emails()
    
    # Choose an email to delete
    choice = input("Enter the indices of the email addresses to delete (comma-separated): ")
    indices = [int(i) for i in choice.split(',')]
    emails_to_delete = [all_emails[i] for i in indices]


    # Delete the email
    for email in emails_to_delete:
        cursor.execute("DELETE FROM emails WHERE email = ?", (email,))
    conn.commit()

    log_info(f"{len(emails_to_delete)} emails deleted: {emails_to_delete}")

def delete_all_emails():
    check = input("Are you sure you want to delete all stored emails? (Enter CONFIRM): ")
    if check != "CONFIRM":
        print("Deletion cancelled.")
        return
    
    cursor.execute("DELETE FROM emails")
    conn.commit()
    log_info("All stored emails have been deleted.")

def add_email():
    email = input("Enter the email address to add: ")
    cursor.execute("INSERT OR IGNORE INTO emails (email) VALUES (?)", (email,))
    conn.commit()
    log_info(f"{email} added to stored emails.")

def update_last_UID():
    # Fetch UID from Imap
    with imaplib.IMAP4_SSL(IMAP_SERVER) as imap:
        imap.login(EMAIL, PASSWORD)
        imap.select("inbox")
        status, messages = imap.uid('search', None, 'ALL')
        uids = messages[0].split()
        last_uid = uids[-1].decode('utf-8')
        print(f"Last UID: {last_uid}")
        print(f"Current last UID: {get_last_uid()}")

        choice = input("Do you want to update the last UID? (Enter 'y' for yes): ")
        if choice != 'y':
            print("Last UID not updated.")
            return
        
        save_last_uid(last_uid)
        log_info(f"Last UID updated to {last_uid}")


# Fetch and process new emails
def process_new_emails():
    with imaplib.IMAP4_SSL(IMAP_SERVER) as imap:
        imap.login(EMAIL, PASSWORD)
        imap.select("inbox")
        
        # Get the last processed UID
        last_uid = get_last_uid()
        search_criteria = f'UID {int(last_uid) + 1}:*' if last_uid else 'ALL'
        
        # Search for new emails
        status, messages = imap.uid('search', None, search_criteria)
        uids = messages[0].split()

        for uid in uids:
            # Fetch the email by UID§
            status, msg_data = imap.uid('fetch', uid, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = msg["From"]
                    sender_email = sender.split('<')[-1].strip('>')

                    # Save sender email to database
                    cursor.execute("INSERT OR IGNORE INTO emails (email) VALUES (?)", (sender_email,))
                    conn.commit()
                    log_info(f"New email processed from {sender_email}")

                    # Send automated reply 
                    send_automated_reply(sender_email)

            # Update the last processed UID
            save_last_uid(uid.decode('utf-8'))
        
        log_info("Processed new emails")

def send_to_subset():
    # Fetch stored emails
    all_emails = view_stored_emails()
    
    # Choose a subset
    print("Please select a subset of emails to send to:")
    print("\tTo send to all stored emails please enter 0")
    print("\tTo send to a selection of emails please enter 1")
    print("\tTo send to all except a selection of emails please enter 2")
    print("\tTo send to the first n emails please enter 3")
    print("\tTo sen to all but the first n emails please enter 4")
    print("\tTo send to the last n emails please enter 5")
    print("\tTo send to a random subset of emails please enter 6")
    print("\tTo exit please enter -1")
    
    choice = input("Enter your choice: ")

    if choice == '0':
        selected_emails = all_emails
    elif choice == '1':
        selected = input("Enter indices of emails to send (comma-separated): ")
        indices = [int(i) for i in selected.split(',')]
        if any(i >= len(all_emails) or i < 0 for i in indices):
            log_error("Invalid indices entered.")
            return
        selected_emails = [all_emails[i] for i in indices]
    elif choice == '2':
        selected = input("Enter indices of emails to exclude (comma-separated): ")
        indices = [int(i) for i in selected.split(',')]
        if any(i >= len(all_emails) or i < 0 for i in indices):
            log_error("Invalid indices entered.")
            return
        selected_emails = [email for i, email in enumerate(all_emails) if i not in indices]
    elif choice == '3':
        n = int(input("Enter the number of emails to send to: "))
        selected_emails = all_emails[:n]
    elif choice == '4':
        n = int(input("Enter the number of emails to exclude: "))
        selected_emails = all_emails[n:]
    elif choice == '5':
        n = int(input("Enter the number of emails to send to: "))
        selected_emails = all_emails[-n:]
    elif choice == '6':
        n = int(input("Enter the number of emails to send to: "))
        selected_emails = random.sample(all_emails, n)
    elif choice == '-1':
        return
    else:
        print("Invalid choice. Please try again.")
        return
    
    # Send to subset
    with smtplib.SMTP(SMTP_SERVER, 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, PASSWORD)

        # Choose a text file to send as the email body
        choice = input("Do you want to send a custom message (enter 0) or a file (enter 1)?: ")
        if choice == '0':
            message = input("Enter your message: ")
            msg = MIMEText(message)
        elif choice == '1':
            filename = input("Enter the name of the file to send as the email body (email_body.txt): ")
            with open(filename, "r") as file:
                msg = MIMEText(file.read())
        else:
            log_error("Invalid choice. Please try again.")
       
        
        subject = input("Enter the subject of the email: ")
        msg["Subject"] = subject
        msg["From"] = EMAIL

        for email in selected_emails:    
            msg["To"] = email
            print(f"Sending email to {email}")
            if MODE == 0:
                print(f"Development Mode: Sending {msg}\n")
            else:
                smtp.sendmail(EMAIL, email, msg.as_string())
            if choice == '0':
                log_info(f"Email with custom message sent to {email}")
            elif choice == '1':
                log_info(f"Email from file {filename} sent to {email}")
    
    print("Emails sent successfully!")



def main():
    try:
        if MODE == 2:
            process_new_emails()
            return
        
        print("--------------- Welcome to AutoMailtion ---------------")
        if MODE == 0: 
            print("Running in Development Mode")
        
        while True:
            print("Please select an option:")
            print("\tTo Process new emails please enter 1")
            print("\tTo view stored emails please enter 2")
            print("\tTo send to a subset of stored mail addresses please enter 3")
            print("\tTo delete an email please enter 4")
            print("\tTo delete all emails please enter 5")
            print("\tTo add an email please enter 6")
            print("\tTo update the last UID please enter 7")
            print("\tTo exit the program please enter 0")
            choice = input("Enter your choice: ")

            if choice == '1':
                process_new_emails()
            elif choice == '2':
                view_stored_emails()
            elif choice == '3':
                send_to_subset()
            elif choice == '4':
                delete_email()
            elif choice == '5':
                delete_all_emails()
            elif choice == '6':
                add_email()
            elif choice == '7':
                update_last_UID()
            elif choice == '0':
                print("Exiting program. Goodbye!")
                log_info("Program exited.")
                break
            else:
                print("Invalid choice. Please try again.")
    except Exception as e:
        log_error(f"An error occurred: {e}")
    finally:
        conn.close()




if __name__ == "__main__":
    main()