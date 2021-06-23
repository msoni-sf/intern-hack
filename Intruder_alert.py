import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def SendMail(ImgFileName, subject, body, to):
    with open(ImgFileName, 'rb') as f:
        img_data = f.read()

    msg = MIMEMultipart()
    msg['subject'] = subject
    user = 'ruchika.team@gmail.com'
    password = 'ahqlqqaaodwmopfp'
    msg['From'] = user
    msg['To'] = to

    text = MIMEText("alert")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(user, password)
    s.send_message(msg, user, to)
    s.quit()

SendMail('pic1.png', "Intruder-alert", "Hey user, This person, tried to log-in", 'sharan6ruchika@gmail.com')
