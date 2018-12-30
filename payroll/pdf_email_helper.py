import smtplib
from email.message import EmailMessage
from threading import Thread
from logzero import logger as l

class Mailer:
    # constractor to pass the email and password when calling this class.
    def __init__(self,email_address,password):
        self.email_address = email_address
        self.password = password
        self.thread_list = []   #this list is used to hold the email addresses if we will send to more than one employee.

    # function for the email informations (from, to, email body)
    def create_msg(self, to, subject, body, file_path=None, file_name=None):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = to
        msg.set_content(body)
        if file_path:       # check if there is an attachment or not
            filename = file_name if file_name else 'report.pdf'     # set the attachment name
            with open(file_path, 'rb') as f:
                msg.add_attachment(f.read(), maintype='pdf', subtype='pdf', filename=filename)
        return msg


    #  informations about the mail server we want to send from
    def _target(self, msg):
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)    #the mail server and the port we used to send the email with.
            server.ehlo()
            server.login(self.email_address, self.password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.close()
            l.info('Email sent succesfully')
        except Exception as e:
            l.error('Email was not sent, the following error occured:\n {}'.format(str(e)))

    #  openning threads to send more than one email in the background and without hanging the application for the user.
    def send_mail(self, msg):
        t = Thread(target=self._target,args=(msg,))
        t.start()
        self.thread_list.append(t)

    #  close all oped threads after sending the mail.
    def join_all_threads(self):
        for t in self.thread_list:
            t.join()
