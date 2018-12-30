import smtplib
from email.mime.text import MIMEText
from threading import Thread
from logzero import logger as l

class Mailer:
    def __init__(self,email_address,password):
        self.email_address = email_address
        self.password = password

    def create_msg(self, to, subject, body):
        msg = MIMEText(body, _charset='UTF-8', _subtype='html')
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = to
        return msg
    
    def send_mail(self, msg):
        t = Thread(target=self._target,args=(msg,))
        t.start()

    def _target(self, msg):
        try:  
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.email_address, self.password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.close()
            l.info('Email sent succesfully')
                
        except Exception as e:  
            l.error('Email was not sent, the following error occured:\n {}'.format(str(e)))

