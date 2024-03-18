from encrypt import SafeFile

if __name__ == "__main__":

    password = b"Haslo1234!"
    path_of_sample_file = ""

    encrypt = SafeFile(
        password=password,
        type_of_crypt="decrypt",
        path=path_of_sample_file
    )
    encrypt.make_crypto()