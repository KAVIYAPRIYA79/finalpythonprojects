import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Database configuration
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345',
    'database': 'TamilNadu_Election_db'  #database name
}

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'kaviyadheepika74@gmail.com'  #Gmail ID
smtp_password = 'vqso cxdc xler hqws'  #password 

def create_connection():
    """Create a connection to MySQL database."""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

def cast_vote(politician_name, voter_email):
    """Cast a vote for a politician and log the action."""
    connection = create_connection()
    if connection is None:
        print("Connection to the database failed.")
        return

    cursor = connection.cursor()
    try:
        # Check if politician exists
        cursor.execute("SELECT * FROM candidates WHERE name = %s", (politician_name,))
        politician = cursor.fetchone()
        if politician is None:
            print(f"Candidate '{politician_name}' does not exist.")
            return

        # Update votes count
        cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE name = %s", (politician_name,))
        connection.commit()
        print(f"Vote cast for {politician_name}")

        # Log the vote
        log_vote(politician_name, voter_email)

        # Send a thank you email
        send_thank_you_email(voter_email, politician_name)

    except Error as e:
        print(f"Error casting vote: {e}")
    finally:
        cursor.close()
        connection.close()

def log_vote(politician_name, voter_email):
    """Log the vote action to a file."""
    voting_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{voting_time} - {voter_email} voted for {politician_name}\n"
    
    try:
        with open('voters_log.txt', 'a') as file:
            file.write(log_entry)
            print(f"Wrote to voters_log.txt: {log_entry.strip()}")
    except IOError as e:
        print(f"Error writing to voters_log.txt: {e}")

def send_thank_you_email(voter_email, politician_name):
    """Send a thank you email to the voter."""
    voting_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = "We appreciate your vote! Thanks for voting!"
    body = f"Dear Voter,\n\nThank you for voting for {politician_name} on {voting_time}. Your support is greatly appreciated and it plays a vital role in our democratic process.\n\nBest regards,\nThe Election Team"

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = voter_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, voter_email, msg.as_string())
            print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    politician_name = input("Enter the candidate's name you want to vote for: ")
    voter_email = input("Enter your email ID: ")
    cast_vote(politician_name, voter_email)
    print("Vote cast successfully.")
