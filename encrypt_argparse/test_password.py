import pytest

from password_validator import Validate
from password_validator import LenghtErrorException, SymbolErrorException, NumberErrorException, LetterErrorException

def test_create():
    password = Validate('Dawid')
    assert password.password == 'Dawid'

def test_lenght_password():
    password = Validate('DawidToMa8Znaków')
    assert password.validate_lenght() == True

def test_wrong_lenght_password():
    with pytest.raises(LenghtErrorException) as message:
        password = Validate('Dawid')
        password.validate_lenght()
        assert message == 'Za krótkie hasło!'

def test_symbol_password():
    password = Validate('Dawid!')
    assert password.validate_symbols() == True

def test_wrong_symbol_password():
    with pytest.raises(SymbolErrorException) as message:
        password = Validate('dawid')
        password.validate_symbols()
        assert message == "Brak znaku specialnego!"

def test_leters_password():
    password = Validate('Dawid')
    assert password.validate_letters() == True

def test_wrong_upper_leters_password():
    with pytest.raises(LetterErrorException) as message:
        password = Validate('dawid')
        password.validate_letters()
        assert message == 'Brak dużej litery!'

def test_wrong_lower_leters_password():
    with pytest.raises(LetterErrorException) as message:
        password = Validate('DAWID')
        password.validate_letters()
        assert message == 'Brak małej litery!'

def test_numbers_password():
    password = Validate('Dawid123')
    assert password.validate_numbers() == True

def test_wrong_numbers_password():
    with pytest.raises(NumberErrorException) as message:
        password = Validate('dawid')
        password.validate_numbers()
        assert message == "Brak cyfry!"

def test_total_password():
    password = Validate('DawidTestDobregoHasla123!')
    assert password.total_result() == True
