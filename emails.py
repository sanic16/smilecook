from flask_mail import Message
from flask import render_template
from dotenv import load_dotenv
from extensions import mail 
import os

load_dotenv()



def send_email(subject, body, recipient):
    msg = Message(
        subject=subject,
        recipients=[recipient],
        sender=os.environ.get('MAIL_DEFAULT_SENDER'),
        body=body
    ) 
    # msg.html = render_template('index.html')
    mail.send(msg)