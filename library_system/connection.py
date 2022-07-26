from collections import namedtuple
from context_mnager import MyManager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jinja2
import smtplib
import ssl
import sqlite3

class DatabaseConection:
    def __init__(self, date, destination: str):
        self.date = date
        self.destination = destination

    def get_data(self):
        data = []
        connection = sqlite3.connect(self.destination)
        with MyManager(connection) as database:
            database.cursor.execute("Select * from books where created_at <= ?", (self.date, ))
            for id_book, title, author, created_at, email, person in database.cursor.fetchall():
                data.append((id_book, title, author, created_at, email, person))

        return data

class CheckSelectedData:
    def __init__(self, selected_date: DatabaseConection):
        self.selected_date = selected_date

    def finder_inforamtion(self):
        person_with_delayed_books = {}
        data = self.selected_date.get_data()
        for items in data:
            Person = namedtuple(
                'Person', 'id_book title author created_at email person'
                )
            selected_person = Person(*items)
            person_with_delayed_books[selected_person.id_book] = (
                    selected_person.title,
                    selected_person.person,
                    selected_person.created_at,
                    selected_person.email
                    )

        return person_with_delayed_books

class SendEmial:

    def render_template(template, **kwargs):
        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('template'))
        templ = jinja_env.get_template(template)

        return templ.render(**kwargs)

    def send_email(
            to,
            password,
            sender,
            subject=None,
            body=None,
            ):

        to_list = [x for x in to if x is not None]
        msg = MIMEMultipart('alternative')
        msg['From'] = sender
        msg['Subject'] = subject
        msg['To'] = ','.join(to)
        msg.attach(MIMEText(body, 'html'))

        smtp_server = 'smtp.gmail.com'
        port = 465
        context = ssl.create_default_context()
        server_python = smtplib.SMTP_SSL(smtp_server, port, context=context)
        server_python.login(sender, password)
        try:
            server_python.sendmail(sender, to_list, msg.as_string())
        finally:
            server_python.quit()

