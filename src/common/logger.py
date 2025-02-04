try:
    from .calendar import Calendar
    from .dtype import classproperty
except ImportError:
    from src.common.calendar import Calendar
    from src.common.dtype import classproperty
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


class Log:

    SENDER:str = 'snob.labwons@gmail.com'
    RECEIVER:str = 'jhlee_0319@naver.com'

    active: bool = True
    title:str = f"{Calendar} Log"
    text:str = ''

    @classmethod
    def append(cls, message:str):
        if cls.active:
            cls.text += message
        return
    
    @classmethod
    def set_title(cls, title:str):
        cls.title = title
        return

    @classmethod
    def send(cls):
        message = MIMEMultipart()
        message['Subject'] = cls.title
        message['From'] = cls.SENDER
        message['To'] = cls.RECEIVER
        message.attach(MIMEText(cls.text))
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.login(cls.SENDER, "puiz yxql tnoe ivaa")
                server.send_message(message)
        except Exception as e:
            return
        return

    @classproperty
    def failcount(cls) -> int:
        return cls.text.count('Fail')