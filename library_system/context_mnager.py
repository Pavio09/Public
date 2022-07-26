import sqlite3

class MyManager:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = None

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()

        self.connection.close()

if __name__ == '__main__':
    destination = ''
    author = 'Henryk Sienkiewicz'
    connection = sqlite3.connect(destination)
    with MyManager(connection) as database:
        database.cursor.execute('Select * from books where author = ?', (author, ))
