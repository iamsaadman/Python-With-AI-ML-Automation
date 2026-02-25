import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time

# ------- Email Configuration -------
sender_email = "saadmansakib34@gmail.com"
password = "pnus uvub cmyt lxhx"  # App password for Gmail

# ------- Collect Recipient Information -------
receiver_email = input("Enter the recipient's email address: ")
name = input("Enter the recipient's name: ")
dob = input("Enter the recipient's date of birth (YYYY-MM-DD): ")

# Parse date
dob_date = datetime.strptime(dob, "%Y-%m-%d")

# ------- Set Time for Email Sending -------
send_hour = int(input("Enter the hour to send the email (0-23): "))
send_minute = int(input("Enter the minute to send the email (0-59): "))

print(f"\nEmail will be sent at {send_hour:02d}:{send_minute:02d} every year on the recipient's birthday.\n")

# To prevent multiple sends in same minute
email_sent_today = False

# -------- Loop to Check Date and Time --------
while True:
    now = datetime.now()
    
    # Check birthday
    is_birthday = (
        now.month == dob_date.month and
        now.day == dob_date.day
    )
    
    # Check time
    is_correct_time = (
        now.hour == send_hour and
        now.minute == send_minute
    )
    
    if is_birthday and is_correct_time and not email_sent_today:
        try:
            # Create message
            body = f"""
🎂 Happy Birthday {name}! 🎉

Wishing you a wonderful day filled with joy, success, and happiness.
May all your dreams come true!

Best wishes ❤️
"""
            msg = MIMEText(body)
            msg['Subject'] = "🎂 Happy Birthday! 🎉"
            msg['From'] = sender_email
            msg['To'] = receiver_email

            # Connect to Gmail
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, password)
                server.send_message(msg)

            print(f"✅ Email sent successfully at {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            email_sent_today = True  # Prevent duplicate sending

        except Exception as e:
            print("❌ Error sending email:", e)

    # Reset flag next day
    if not is_birthday:
        email_sent_today = False

    print("⏳ Waiting... Current time:", now.strftime("%Y-%m-%d %H:%M:%S"))
    
    time.sleep(60)  # Check every minute
   