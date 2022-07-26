import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from functools import  namedtuple

class WrongTypeOfCoding(Exception):
    pass

class MyContext:
    def __init__(self, file: str, method: str):
        self.file_obj = open(file, method)

    def __enter__(self):
        return self.file_obj

    def __exit__(self, type, value, traceback):
        self.file_obj.close()

class SafeFile:
    """Encoding or decoding of data within a designated file
    """
    def __init__(self, password: str, type_of_crypt: str):
        if type_of_crypt not in ['encrypt', 'decrypt']:
            raise WrongTypeOfCoding("Wrong coding option selected")
        else:
            self.type_of_crypt = type_of_crypt
        self.password = password
        self.text = None

    def set_pbkdf(self):
        """Establishment of a key derivation function based on a password

        Returns:
            object: fernet token based on encoding binary data on URL-safe base64-encoded key
        """
        salt = b'test12341234'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000
        )

        fernet = Fernet(base64.urlsafe_b64encode(kdf.derive(self.password)))

        return fernet

    def encrypt(self):
        """Encrypted data

        Returns:
            str: A secure message which is referred to Fernet token
        """
        fernet = self.set_pbkdf()
        safe_string = fernet.encrypt(self.text.encode('utf8'))

        return safe_string

    def decrypt(self):
        """Decrypted data

        Returns:
            str: The original string
        """
        fernet = self.set_pbkdf()
        decrypt_string = fernet.decrypt(self.text).decode('utf8')

        return decrypt_string

    def crypto(self):
        """Option to select action on a file

        Returns:
            method: activates the selected method
        """
        if self.type_of_crypt == 'encrypt':
            return self.encrypt()
        elif self.type_of_crypt == 'decrypt':
            return self.decrypt()

    def read_file(self, selected_type_of_read: str, path: str):
        """Reads the contents of a file

        Args:
            selected_type_of_read (str): mode
            path (str): path to file

        Returns:
            str: file content
        """
        with MyContext(path, selected_type_of_read) as file:
            line_to_crypt = file.readline()

        return line_to_crypt

    def write_file(self, selected_type_of_write: str, path: str, safe_text: str):
        """_summary_

        Args:
            selected_type_of_write (str): mode
            path (str): path
            safe_text (str): secured file data
        """
        with MyContext(path, selected_type_of_write) as file_out:
            file_out.write(safe_text)

    def make_crypto(self, path: str):
        """Performs encoding or decoding based on the selected file

        Args:
            path (str): path to file
        """
        setting = namedtuple('Setting', ['reader', 'writer'])
        mapping_type_of_coding = {
            'encrypt':setting('r', 'wb'),
            'decrypt':setting('rb', 'w')
        }
        selection = mapping_type_of_coding[self.type_of_crypt]
        self.text = self.read_file(selected_type_of_read=selection.reader, path=path)

        safe_text = self.crypto()

        self.write_file(selected_type_of_write=selection.writer,
                        path=path,
                        safe_text=safe_text)