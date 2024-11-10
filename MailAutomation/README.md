# AutoMailtion

(Disclaimer: This README was partially written by ChatGPT)

AutoMailtion is a script that automates email replies, manages email lists, and processes incoming emails from an IMAP server. This README provides instructions for setup and usage.

## Setup

1. **Dependencies:** Ensure you have imaplib, smtplib, sqlite3, and dotenv installed. These are part of Python’s standard library except for dotenv, which can be installed via pip:
```bash
   pip install python-dotenv
```


3. **Environment Variables:** Create a .env file in the project directory with the following variables:
   - EMAIL=\<your-email@example.com>
   - PASSWORD=\<your-email-password>
   - IMAP_SERVER=\<your-imap-server>
   - SMTP_SERVER=\<your-smtp-server>

4. **Auto-Reply Message and Subject:** Configure the AUTOREPLY_FILE and AUTOREPLY_SUBJECT variables in the script.
   - AUTOREPLY_FILE should contain the path to a text file (e.g., autoreply1.txt) with the content of the automatic reply.
   - AUTOREPLY_SUBJECT is the subject line for the auto-reply email.

5. **Initialize Last UID:**
   - The script uses UID_FILE to store the last processed email's UID, ensuring it doesn’t reprocess old emails.
   - You may need to update this UID initially to avoid processing all previous emails. Run the update_last_UID function to set the last UID based on current emails in your inbox.

## Usage

1. **Running the Script:** Run the script by executing:

```bash
python automailtion.py
```

You’ll be presented with several options to manage email processing and auto-reply functionality. 2. **Main Functions:**

- Process new emails: Fetches new emails, sends auto-replies, and stores sender addresses in the database.
- View stored emails: Lists all stored email addresses.
- Send to subset of stored mail addresses: Allows you to select and email a subset of stored addresses with a custom or preloaded message.
- Delete an email: Select and delete specific email addresses from storage.
- Delete all emails: Deletes all stored email addresses.
- Update the last UID: Updates the last UID to the current email list, ensuring no old emails are reprocessed.

3. Exiting the Program: Enter 0 to exit the program.

## Additional Notes

**Database:** Stored emails are saved in an SQLite database (emails.db). The script will create this database automatically if it doesn’t exist.

**Configuration Changes:** Modify AUTOREPLY_FILE, AUTOREPLY_SUBJECT, or other configuration settings as needed to customize the behavior.

This script is a flexible, command-line tool for managing incoming emails, replying automatically, and organizing email addresses for targeted communication. Enjoy automating your inbox!
