from abc import ABC, abstractmethod

class LenghtErrorException(Exception):
    pass

class SymbolErrorException(Exception):
    pass

class NumberErrorException(Exception):
    pass

class LetterErrorException(Exception):
    pass

class PasswordValidate(ABC):
    @abstractmethod
    def validate_lenght(self):
        pass
    @abstractmethod
    def validate_symbols(self):
        pass
    @abstractmethod
    def validate_numbers(self):
        pass

class Validate(PasswordValidate):
    def __init__(self, password: str):
        self.password = password

    def validate_lenght(self):
        if len(self.password) < 8:
            raise LenghtErrorException("Too short a password!")

        return True

    def validate_symbols(self):
        if not any([x for x in self.password if x in '!@#$%^&*()']):
            raise SymbolErrorException("Missing special symbol!")

        return True

    def validate_letters(self):
        if not any([x for x in self.password if x.isupper()]):
            raise LetterErrorException("Missing capital letter!")
        if not any([x for x in self.password if x.islower()]):
            raise LetterErrorException("Missing small letter!")
        return True

    def validate_numbers(self):
        if not any([x for x in self.password if x.isnumeric()]):
            raise NumberErrorException("Missing number!")

        return True

    def total_result(self):
        if all([
            self.validate_symbols(),
            self.validate_lenght(),
            self.validate_numbers(),
            self.validate_letters()
        ]): return True