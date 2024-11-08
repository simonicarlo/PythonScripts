import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.header import decode_header
import sqlite3
import os
from dotenv import load_dotenv
import random

# Email and IMAP Configuration
load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
UID_FILE = "last_uid.txt"

AUTOREPLY_FILE = "autoreply1.txt"
AUTOREPLY_SUBJECT = "Danke für deine Email!"

# SQLite setup for storing emails
conn = sqlite3.connect('emails.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS emails (email TEXT UNIQUE)")

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

# Send automated reply
def send_automated_reply(sender_email):
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

        smtp.sendmail(EMAIL, sender_email, msg.as_string())


# View stored emails
def view_stored_emails():
    cursor.execute("SELECT email FROM emails")
    all_emails = [row[0] for row in cursor.fetchall()]
    
    print("Stored Emails:")
    for idx, email in enumerate(all_emails):
        print(f"{idx}: {email}")

def delete_email():
    # Fetch stored emails
    cursor.execute("SELECT email FROM emails")
    all_emails = [row[0] for row in cursor.fetchall()]
    
    print("Stored Emails:")
    for idx, email in enumerate(all_emails):
        print(f"{idx}: {email}")
    
    # Choose an email to delete
    choice = input("Enter the indices of the email addresses to delete (comma-separated): ")
    indices = [int(i) for i in choice.split(',')]
    emails_to_delete = [all_emails[i] for i in indices]


    # Delete the email
    for email in emails_to_delete:
        cursor.execute("DELETE FROM emails WHERE email = ?", (email,))
    conn.commit()
    print(f'{len(emails_to_delete)} emails have been deleted.')

def delete_all_emails():
    check = input("Are you sure you want to delete all stored emails? (Enter CONFIRM): ")
    if check != "CONFIRM":
        print("Deletion cancelled.")
        return
    
    cursor.execute("DELETE FROM emails")
    conn.commit()
    print("All stored emails have been deleted.")

def add_email():
    email = input("Enter the email address to add: ")
    cursor.execute("INSERT OR IGNORE INTO emails (email) VALUES (?)", (email,))
    conn.commit()
    print(f'{email} has been added to the stored emails.')

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

                    # Send automated reply 
                    send_automated_reply(sender_email)

            # Update the last processed UID
            save_last_uid(uid.decode('utf-8'))
        
        print("New emails processed successfully!")

def send_to_subset():
    # Fetch stored emails
    cursor.execute("SELECT email FROM emails")
    all_emails = [row[0] for row in cursor.fetchall()]
    
    print("Stored Emails:")
    for idx, email in enumerate(all_emails):
        print(f"{idx}: {email}")
    
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
        selected_emails = [all_emails[i] for i in indices]
    elif choice == '2':
        selected = input("Enter indices of emails to exclude (comma-separated): ")
        indices = [int(i) for i in selected.split(',')]
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
        else:
            filename = input("Enter the name of the file to send as the email body (email_body.txt): ")
            with open(filename, "r") as file:
                msg = MIMEText(file.read())
       
        
        subject = input("Enter the subject of the email: ")
        msg["Subject"] = subject
        msg["From"] = EMAIL

        for email in selected_emails:    
            msg["To"] = email
            print(f"Sending email to {email}")
            smtp.sendmail(EMAIL, email, msg.as_string())
    
    print("Emails sent successfully!")



def main():
    print("--------------- Welcome to AutoMailtion ---------------")

    while True:
        print("Please select an option:")
        print("\tTo Process new emails please enter 1")
        print("\tTo view stored emails please enter 2")
        print("\tTo send to a subset of stored mail addresses please enter 3")
        print("\tTo delete an email please enter 4")
        print("\tTo delete all emails please enter 5")
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
        elif choice == '0':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")




if __name__ == "__main__":
    main()