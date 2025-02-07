from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP


class eMail(MIMEMultipart):

    _context:str = ''

    def __init__(self):
        super().__init__()
        self['From'] = 'snob.labwons@gmail.com'
        self['To'] = 'jhlee_0319@naver.com'
        return

    @property
    def subject(self) -> str:
        return self['Subject']

    @subject.setter
    def subject(self, subject:str):
        self['Subject'] = subject

    @property
    def sender(self):
        return self['From']

    @sender.setter
    def sender(self, sender:str):
        self['From'] = sender

    @property
    def receiver(self):
        return self['To']

    @receiver.setter
    def receiver(self, receiver:str):
        self['To'] = receiver

    @property
    def context(self) -> str:
        return self._context

    @context.setter
    def context(self, context:str):
        self._context = context

    def send(self):
        self.attach(MIMEText(self.context))
        with SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(self.sender, "puiz yxql tnoe ivaa")
            server.send_message(self)
        return


if __name__ == "__main__":
    mail = eMail()
    mail.subject = "Test Email"
    mail.context = "This is a test mail"
    mail.send()