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



# Load environment variables
load_dotenv()

# Mode of Operation
# 0: Development Mode - CLI for testing (no email sending)
# 1: Manual Mode - CLI for processing emails
# 2: Automated Mode - Process new emails and send automated replies (setup in cron job)

MODE = 1
MODE_DESCRIPTION = {0: "Development", 1: "Manual", 2: "Automated"}
current_mode = MODE_DESCRIPTION.get(MODE, "Unknown")

# Last UID Configuration
UID_FILE = os.path.join(os.path.dirname(__file__), "last_uid.txt")

# Logging Configuration
LOG_FILE = os.path.join(os.path.dirname(__file__), "history.log")
ENABLE_LOGGING = True

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [Mode: %(mode)s] - %(message)s",
)

# Automated Reply Configuration
AUTOREPLY_FILE = os.path.join(os.path.dirname(__file__), "autoreply1.txt")
AUTOREPLY_SUBJECT = "Danke für deine Email!"

# Email and IMAP Configuration
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")

# Database Configuration
# SQLite setup for storing emails
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "emails.db"))
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS emails (email TEXT UNIQUE)")


# ANSI Color Codes for terminal text
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    END = '\033[0m'

# Add color to string
def color_text(text, color):
    return f"{color}{text}{Color.END}"

# Print with color
def color_print(text, color):
    print(f"{color}{text}{Color.END}")

# Logging
def log_info(message):
    print("\n" + message)
    if ENABLE_LOGGING:
        logging.info(message, extra={'mode': current_mode})

def log_error(message):
    color_print(f'\nERROR: {message}', Color.RED)
    if ENABLE_LOGGING:
        logging.info(message, extra={'mode': current_mode})

# Function to get last UID
def get_last_uid():
    if os.path.exists(UID_FILE):
        with open(UID_FILE, 'r') as file:
            return file.read().strip()
    return -1

# Function to save last UID
def save_last_uid(uid):
    with open(UID_FILE, 'w') as file:
        file.write(uid)
    log_info(f"Last UID saved as {uid}")

def view_new_emails():
    with imaplib.IMAP4_SSL(IMAP_SERVER) as imap:
        imap.login(EMAIL, PASSWORD)
        imap.select("inbox")

        last_uid = get_last_uid()
        next_uid = int(last_uid) + 1 if last_uid else 1

        search_criteria = f'UID {next_uid}:*' if last_uid else 'ALL'
        status, messages = imap.uid('search', None, search_criteria)
        uids = messages[0].split()
        if uids[0].decode('utf-8') == last_uid:
            print("No new emails.")
            return

        print(f"{'UID':<7} {'From':<50} {'Subject'}")
        print("="*100)

        for uid in uids:
            status, msg_data = imap.uid('fetch', uid, '(RFC822)')
            for returned_mail in msg_data:
                if isinstance(returned_mail, tuple):
                    msg = email.message_from_bytes(returned_mail[1]) # returned_mail[0] is just the UID
                    subject = msg["Subject"]
                    sender = msg["From"]
                    print(f"{uid.decode('utf-8'):<7} {sender:<50} {subject}")

# Send automated reply
def send_automated_reply(sender_email):

    if not os.path.exists(AUTOREPLY_FILE):
        log_error(f"Automated reply file {AUTOREPLY_FILE} not found.")
        raise FileNotFoundError("Automated reply file not found.")

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
            print(f"\nDevelopment Mode - Sending: \n{msg}\n")
        else: 
            smtp.sendmail(EMAIL, sender_email, msg.as_string())
    log_info(f"Sent automated reply to {sender_email}")


# View stored emails
def view_stored_emails():
    cursor.execute("SELECT email FROM emails")
    all_emails = [row[0] for row in cursor.fetchall()]
    
    color_print("\nStored Emails:",Color.CYAN)
    for idx, email in enumerate(all_emails):
        print(f"{color_text(idx,Color.CYAN)}: {email}")

    return all_emails

def delete_email():
    # Fetch stored emails
    all_emails = view_stored_emails()
    
    # Choose an email to delete
    choice = input(color_text("\nEnter the indices of the email addresses to delete (comma-separated): ",Color.GREEN))
    indices = [int(i) for i in choice.split(',')]
    emails_to_delete = [all_emails[i] for i in indices]


    # Delete the email
    for email in emails_to_delete:
        cursor.execute("DELETE FROM emails WHERE email = ?", (email,))
    conn.commit()

    log_info(f"{len(emails_to_delete)} emails deleted: {emails_to_delete}")

def delete_all_emails():
    check = input(color_text("\nAre you sure you want to delete all stored emails? (Enter \"CONFIRM\"): ",Color.RED))
    if check != "CONFIRM":
        print("Deletion cancelled.")
        return
    
    cursor.execute("DELETE FROM emails")
    conn.commit()
    log_info("All stored emails have been deleted.")

def add_email():
    email = input(color_text("\nEnter the email address to add: ",Color.GREEN))
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
        print(f"\nLast UID: {last_uid}")
        print(f"Current last UID: {get_last_uid()}")

        choice = input(color_text("\nDo you want to update the last UID? (Enter 'y' for yes): ",Color.GREEN))
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
        next_uid = int(last_uid) + 1 if last_uid else 1

        search_criteria = f'UID {next_uid}:*' if last_uid else 'ALL'
        # Search for new emails
        status, messages = imap.uid('search', None, search_criteria)
        uids = messages[0].split()
        if uids[0].decode('utf-8') == last_uid:
            log_info("No new emails to process.")
            return


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
                    log_info(f"New email processed from {sender_email} (UID: {uid.decode('utf-8')})")

                    # Send automated reply
                    try:
                        send_automated_reply(sender_email)
                    except FileNotFoundError as e:
                        return
                    
            # Update the last processed UID
            save_last_uid(uid.decode('utf-8'))
        
        log_info("Processed new emails")

def send_to_subset():
    # Fetch stored emails
    all_emails = view_stored_emails()
    
    # Choose a subset
    while True:
        color_print("\nPlease select a subset of emails to send to:\n",Color.CYAN)
        print(f"\tTo send to {color_text('all stored',Color.CYAN)} emails please enter {color_text('1',Color.GREEN)}")
        print(f"\tTo send to {color_text('a selection',Color.CYAN)} of emails please enter {color_text('2',Color.GREEN)}")
        print(f"\tTo send to {color_text('all except a selection',Color.CYAN)} of emails please enter {color_text('3',Color.GREEN)}")
        print(f"\tTo send to the {color_text('first n emails',Color.CYAN)} please enter {color_text('4',Color.GREEN)}")
        print(f"\tTo send to {color_text('all but the first n emails',Color.CYAN)} please enter {color_text('5',Color.GREEN)}")
        print(f"\tTo send to the {color_text('last n emails',Color.CYAN)} please enter {color_text('6',Color.GREEN)}")
        print(f"\tTo send to a {color_text('random subset',Color.CYAN)} of emails please enter {color_text('7',Color.GREEN)}")
        print(f"\tTo {color_text('exit',Color.CYAN)} please enter 0")
        
        choice = input(color_text("\nEnter your choice: ",Color.GREEN))

        if choice == '1':
            selected_emails = all_emails
            break
        elif choice == '2':
            selected = input(color_text("Enter indices of emails to send (comma-separated): ",Color.GREEN))
            indices = [int(i) for i in selected.split(',')]
            if any(i >= len(all_emails) or i < 0 for i in indices):
                log_error("Invalid indices entered.")
                return
            selected_emails = [all_emails[i] for i in indices]
            break
        elif choice == '3':
            selected = input(color_text("Enter indices of emails to exclude (comma-separated): ",Color.GREEN))
            indices = [int(i) for i in selected.split(',')]
            if any(i >= len(all_emails) or i < 0 for i in indices):
                log_error("Invalid indices entered.")
                return
            selected_emails = [email for i, email in enumerate(all_emails) if i not in indices]
            break
        elif choice == '4':
            n = int(input(color_text("Enter the number of emails to send to: ",Color.GREEN)))
            selected_emails = all_emails[:n]
            break
        elif choice == '5':
            n = int(input(color_text("Enter the number of emails to exclude: ",Color.GREEN)))
            selected_emails = all_emails[n:]
            break
        elif choice == '6':
            n = int(input(color_text("Enter the number of emails to send to: ",Color.GREEN)))
            selected_emails = all_emails[-n:]
            break
        elif choice == '7':
            n = int(input(color_text("Enter the number of emails to send to: ")))
            selected_emails = random.sample(all_emails, n)
            break
        elif choice == '0':
            return
        else:
            color_print("\nInvalid choice. Please try again.",Color.YELLOW)
    
    print(f"\nSelected Emails: {selected_emails}")

    # Send to subset
    with smtplib.SMTP(SMTP_SERVER, 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, PASSWORD)

        # Choose a text file to send as the email body
        while True:
            option = input(color_text("\nDo you want to send a custom message (enter 0) or a file (enter 1)?: ",Color.GREEN))
            if option == '0':
                message = input(color_text("Enter your message: ",Color.GREEN))
                break
            elif option == '1':
                filename = input(color_text("Enter the name of the file to send as the email body (email_body.txt): ",Color.GREEN))
                if not os.path.exists(filename):
                    log_error(f"File {filename} not found.")
                    continue
                break
            else:
                color_print("\nInvalid choice. Please try again.",Color.YELLOW)
       
        
        subject = input(color_text("Enter the subject of the email: ",Color.GREEN))
        

        for email in selected_emails:    
            # Had to reacrete msg here to avoid "stacking" of emails
            if option == '0':
                msg = MIMEText(message)
            elif option == '1':
                with open(filename, "r") as file:
                    msg = MIMEText(file.read())
            else:
                log_error("send_to_subset: Invalid option selected.")
                return
            msg["Subject"] = subject
            msg["From"] = EMAIL
            msg["To"] = email
            
            if MODE == 0:
                print(f"\nDevelopment Mode - Sending: \n{msg}\n")
            else:
                smtp.sendmail(EMAIL, email, msg.as_string())
            if option == '0':
                log_info(f"Email with custom message sent to {email}")
            elif option == '1':
                log_info(f"Email from file {filename} sent to {email}")
    
    log_info("Emails sent successfully!")



def main(rec = False):
    if MODE == 2:
        process_new_emails()
        return
    
    if not rec:
        color_print("\n--------------- Welcome to AutoMailtion ---------------\n",Color.PURPLE)
        if MODE == 0: 
            color_print("Running in Development Mode",Color.YELLOW)
    
    while True:
        color_print("\nPlease select an option:\n",Color.CYAN)
        print(f"\tTo {color_text('process new emails',Color.CYAN)} please enter {color_text('1',Color.GREEN)}")
        print(f"\tTo {color_text('view stored emails',Color.CYAN)} please enter {color_text('2',Color.GREEN)}")
        print(f"\tTo {color_text('send to a subset',Color.CYAN)} of stored mail addresses please enter {color_text('3',Color.GREEN)}")
        print(f"\tTo {color_text('delete',Color.CYAN)} an email please enter {color_text('4',Color.GREEN)}")
        print(f"\tTo {color_text('delete all',Color.CYAN)} emails please enter {color_text('5',Color.GREEN)}")
        print(f"\tTo {color_text('add',Color.CYAN)} an email please enter {color_text('6',Color.GREEN)}")
        print(f"\tTo {color_text('view new emails',Color.CYAN)} please enter {color_text('7',Color.GREEN)}")
        print(f"\tTo {color_text('update last UID',Color.CYAN)} please enter {color_text('8',Color.GREEN)}")
        print(f"\tTo {color_text('exit',Color.CYAN)} the program please enter {color_text('0',Color.GREEN)}")
        
        choice = input(color_text("\nEnter your choice: ",Color.GREEN))

        if choice == '1':
            process_new_emails()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '2':
            view_stored_emails()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '3':
            send_to_subset()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '4':
            delete_email()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '5':
            delete_all_emails()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '6':
            add_email()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '7':
            view_new_emails()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '8':
            update_last_UID()
            input(color_text("\nPress Enter to continue",Color.CYAN))
        elif choice == '0':
            color_print("\n--------------- Exiting program. Goodbye! ---------------",Color.PURPLE)
            log_info("Program exited.")
            break
        else:
            color_print("\nInvalid choice. Please try again.",Color.YELLOW)





if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"An error occurred: {e}")
    finally:
        conn.close()

    