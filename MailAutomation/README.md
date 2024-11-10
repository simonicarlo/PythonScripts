# AutoMailtion

(Disclaimer: This README was partially written by ChatGPT)

AutoMailtion is an automated email processing and response application designed for managing incoming emails, storing sender addresses, and sending custom automated replies. It operates in three modes: Development (for testing), Manual (for CLI-based email processing), and Automated (for scheduled email processing and replies via cron jobs).

## Features

- Automated email processing and responses
- Email storage and management via SQLite database
- Flexible email sending options to specific or random subsets of stored addresses
- UID tracking to prevent re-processing emails
- Basic Logging Functionality
- Manual, Automated and Developement Mode

## Setup

1. **Install Dependencies:** Ensure you have python-dotenv and sqlite3 installed:
   ```bash
   pip install python-dotenv
   ```
2. **Configure Environment Variables:**

Create a .env file in the root directory with the following:

- EMAIL=\<your_email@example.com\>
- PASSWORD=\<your_email_password\>
- IMAP_SERVER=\<imap.yourmail.com\>
- SMTP_SERVER=\<smtp.yourmail.com\>

Then choose the Operation Mode and enable/disable logging by changeing MODE and ENABLE_LOGGING in the code.

3. **Configure Auto-Reply Content:**

   - Auto-Reply Message: Create a text file containing the message for automated replies and modify the AUTOREPLY_FILE in the code.
   - Auto-Reply Subject: Modify AUTOREPLY_SUBJECT in the code if a different subject line is preferred.

4. **Initialize the UID:**
   - To avoid processing all historical emails, initialize the last_uid value.
   - Run update_last_UID() in Manual mode, view the most recent UID, and confirm if you wish to save it as the starting UID.

## Usage

AutoMailtion supports three modes of operation, configured via the MODE variable:

- **Development Mode (MODE=0):** For testing; does not send emails.
- **Manual Mode (MODE=1):** Use CLI to process emails, view stored addresses, and manage UIDs.
- **Automated Mode (MODE=2):** Automatically processes new emails and sends responses, ideal for scheduling via cron.

### Running the Application

To start the application, run:

```bash
python automailtion.py
```

### Main Operations

Once started, use the menu options to:

1. Process New Emails - Processes all emails received since the last UID.
2. View Stored Emails - Lists all saved sender emails.
3. Send to Subset - Send custom or file-based emails to specific or random groups of stored addresses.
4. Delete Emails - Delete one or multiple saved email addresses.
5. Delete All Emails - Clear all stored addresses.
6. Add Email - Manually add an email address to the database.
7. Update Last UID - Update the last UID for email processing.

To exit the program enter '0' in the selection.

### Logging

All actions and errors are logged to history.log if logging is enabled (ENABLE_LOGGING=True).

## Notes

- **Database:** The application uses SQLite (emails.db) to store unique email addresses.
- **Logging:** Adjust log settings as desired, with logs saved to history.log.
