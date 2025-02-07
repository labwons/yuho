from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP


class eMail(MIMEMultipart):

    SENDER:str = 'snob.labwons@gmail.com'
    ATTACH:str = ''

    def __init__(self, subject:str, to:str):
        super().__init__()
        self['Subject'] = subject
        self['From'] = self.SENDER
        self['To'] = to
        return

    @property
    def attachment(self) -> str:
        return self.ATTACH

    @attachment.setter
    def attachment(self, attachment:str):
        self.ATTACH = attachment

    def send(self):
        self.attach(MIMEText(self.attachment))
        with SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(self.SENDER, "puiz yxql tnoe ivaa")
            server.send_message(self)
        return

