from collections import namedtuple
from connection import CheckSelectedData, SendEmial, DatabaseConection

destination = ""
sender = ""
connection = CheckSelectedData(DatabaseConection(date='2021-04-21', destination=destination))
selected_persons = connection.finder_inforamtion()

for person in selected_persons.values():
    Person = namedtuple('Person', 'book name created_at email')
    to_person = Person(*person)
    jinja_var = {
                'name': "".join(to_person.name.split(" ")[0]),
                'book_name': to_person.book,
                'date': "".join(to_person.created_at.split(" ")[0])
            }
    email = to_person.email
    html = SendEmial.render_template('content.html', **jinja_var)
    subject = 'Passive aggressive przypomnienie :)'
    SendEmial.send_email(to = email, sender=sender,subject = subject, body=html)