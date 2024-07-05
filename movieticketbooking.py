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
    'database': 'movies_tickectbooking_db'
}

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'kaviyadheepika74@gmail.com'  # Gmail ID
smtp_password = 'vqso cxdc xler hqws'  # Use the app-specific password here

# Predefined data
screens = [1, 2, 3, 4]
movies = ['Inception', 'Interstellar', 'The Dark Knight', 'Dunkirk', 'Tenet']
showtimes = ['4:00 PM', '7:00 PM', '10:00 AM', '5:00 PM','5:00 PM']

def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None

def display_options():
    print("Available screens:")
    for screen in screens:
        print(f"Screen {screen}")

    print("\nAvailable movies:")
    for movie in movies:
        print(movie)

    print("\nAvailable showtimes:")
    for showtime in showtimes:
        print(showtime)

def book_tickets(movie_name, screen, showtime, num_tickets, user_email):
    connection = create_connection()
    if connection is None:
        print("Connection to the database failed.")
        return

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT available_tickets FROM movies WHERE name = %s AND screen = %s AND showtime = %s",
                       (movie_name, screen, showtime))
        result = cursor.fetchone()
        if result is None:
            print(f"Movie '{movie_name}' on screen '{screen}' at '{showtime}' does not exist.")
            return

        available_tickets = result[0]
        if available_tickets < num_tickets:
            print(f"Not enough tickets available. Only {available_tickets} tickets left.")
            return

        ticket_price = 190.00  # Example ticket price
        gst_rate = 0.18  # 18% GST
        total_price = num_tickets * ticket_price * (1 + gst_rate)

        cursor.execute("UPDATE movies SET available_tickets = available_tickets - %s WHERE name = %s AND screen = %s AND showtime = %s",
                       (num_tickets, movie_name, screen, showtime))
        connection.commit()
        print(f"{num_tickets} tickets booked for '{movie_name}' on screen '{screen}' at '{showtime}'")

        log_booking(movie_name, screen, showtime, num_tickets, user_email, total_price)
        send_booking_email(user_email, movie_name, screen, showtime, num_tickets, total_price)

    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def log_booking(movie_name, screen, showtime, num_tickets, user_email, total_price):
    booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("Logging booking in moviebooking_log.txt")
    with open('moviebooking_log.txt', 'a') as file:
        file.write(f"{booking_time} - {user_email} booked {num_tickets} tickets for {movie_name} on screen {screen} at {showtime}. Total price: {total_price}\n")
        print(f"Wrote to moviebooking_log.txt: {booking_time} - {user_email} booked {num_tickets} tickets for {movie_name} on screen {screen} at {showtime}. Total price: {total_price}")

def send_booking_email(user_email, movie_name, screen, showtime, num_tickets, total_price):
    booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = "Cinema Ticket Reservation Confirmation"
    body = f"Thank you for your reservation of {num_tickets} tickets for '{movie_name}' on screen {screen} at {showtime}. Your booking was made at {booking_time}.\nThe total amount payable, including GST, is {total_price:.2f}."


    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, user_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    display_options()
    movie_name = input("Enter the movie name: ")
    screen = int(input("Enter the screen number: "))
    showtime = input("Enter the showtime: ")
    num_tickets = int(input("Enter the number of seats you want to book: "))
    user_email = input("Enter your email address: ")
    book_tickets(movie_name, screen, showtime, num_tickets, user_email)
    print(" Movie Ticket Booking process completed successfully.")
