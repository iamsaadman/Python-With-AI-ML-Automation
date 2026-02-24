# Automatic Birthday Email Sender
import smtplib

# Module for sending emails
from email.mime.text import MIMEText 

# To create email messages with attachments (if needed in the future)

sender_email = "saadmansakib34@gmail.com"

#Sender's email address (must be same used to generate app password)
password = "pnus uvub cmyt lxhx"

#16 character app password generated from Gmail account for authentication

reciever_email = input("Enter the recipient's email address: ")
#Recipient's email address input from user

name = input("Enter the recipient's name: ")
#Recipient's name input from user

msg = MIMEText(f"🎂love you,  {name}! Wishing you a wonderful day filled with joy and happiness!🥳I wish you all the best!🙌")

#Email message content with personalized name

msg['Subject'] = "🎂Happy Birthday!🥳"
#Email subject line

msg['From'] = sender_email
#Email sender address

msg['To'] = reciever_email
#Email recipient address


server = smtplib.SMTP('smtp.gmail.com', 587)
#Connecting to Gmail's SMTP server on port 587
server.starttls()
#Starting TLS encryption for secure email transmission
server.login(sender_email, password)
#Logging in to the email account using sender's email and app password
server.send_message(msg)
#Sending the email message
print("Email sent successfully!")
#Confirmation message after email is sent
server.quit()
#Closing the connection to the SMTP server
