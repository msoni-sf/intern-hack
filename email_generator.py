import smtplib
from email.message import EmailMessage
import math, random


def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def email_alert(subject, body, to):
	msg = EmailMessage()
	msg.set_content(body)
	msg['subject']=subject
	msg['to']=to
	user = 'ruchika.team@gmail.com'
	msg['from']=user
	password = 'ahqlqqaaodwmopfp'
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(user, password)
	server.send_message(msg)
	server.quit()

if __name__ == '__main__':
    getotp = generateOTP();
    email_alert('One-time OTP for Inern-Hackathon Project', 'Hey user, your OTP is as follows: '+getotp, 'manansoni1399@gmail.com')
