import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class Config(object):

    # HOST = os.getenv("sds_host", "10.10.6.2")
    # PORT = os.getenv("sds_port", 3306)
    # USER = os.getenv("sds_user", "root")
    # PASS = os.getenv("sds_pass", "123456")

    RECEIVER = os.getenv("email_receive", "*")
    SENDER = os.getenv("email_send", "*")
    EPASS = os.getenv("email_pass", "*")
    MAILSERVER = os.getenv("email_server", "*")
    MAILPORT = os.getenv("email_port", 465)

class Email:

    def __init__(self, mailserver, mailport, sender, pwd, recevier):
        self.mailserver = mailserver
        self.mailport = mailport
        self.sender = sender
        self.pwd = pwd
        self.receiver = recevier

    def txt_email(self, subject, text):
        message = MIMEText(text, "plain", 'utf-8')
        message['From'] = Header('监控报告', 'utf-8')
        message['To'] = Header('监控人','utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        smtpObj = smtplib.SMTP_SSL(self.mailserver, self.mailport)
        smtpObj.login(self.sender, self.pwd)
        smtpObj.sendmail(self.sender, self.receiver, message.as_string())

    def fig_email(self, subject , text, pic):
        message = MIMEMultipart()
        message["From"] = Header('监控报告', 'utf-8')
        message["To"] = Header('监控人', 'utf-8')
        message["Subject"] = Header(subject, 'utf-8')
        message.attach(MIMEText(text, "plain", 'utf-8'))
        with open(pic, 'rb') as f:
            attPIC = MIMEBase('image','jpg', filename = pic)
            attPIC.add_header('Content-Disposition','attachment',filename=pic)
            attPIC.add_header('Content-ID','<0>')
            attPIC.add_header('X-Attachment-Id', '0')
            attPIC.set_payload(f.read())
            encoders.encode_base64(attPIC)
            message.attach(attPIC)
        smtpObj = smtplib.SMTP_SSL(self.mailserver, self.mailport)
        smtpObj.login(self.sender, self.pwd)
        smtpObj.sendmail(self.sender, self.receiver, message.as_string())