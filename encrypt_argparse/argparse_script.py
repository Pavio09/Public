import argparse
import os
from encrypt import SafeFile
from password_validator import Validate

parser = argparse.ArgumentParser(description="Keep my secrets safe!")

help_mode = """encrypt given file or files
                decrypt encrypted file or files
                append -> decrypt file, append text and encrypt the file again"""

parser.add_argument('-m',
                    '--mode',
                    choices=['encrypt','decrypt','append'],
                    help=help_mode)

parser.add_argument('-p',
                    '--password',
                    help='Enter password')

parser.add_argument('-v',
                    '--verbose')

parser.add_argument('--file',
                    action='append',
                    help='List of files to processing')

parser.add_argument('--folder',
                    action='append',
                    help='Path to folder with files to be processed')

args = parser.parse_args()
valid_password = Validate(args.password).total_result()

if valid_password:
    bytes_password = bytes(args.password, "UTF-8")

encrypt = SafeFile(
                password=bytes_password,
                type_of_crypt=args.mode,
                )

if args.mode is not None:
    if args.file is not None:
        encrypt.make_crypto(path=args.file[0])
    if args.folder is not None:
        files = [encrypt.make_crypto(path=f"{args.folder[0]}\\{file}") for file in os.listdir(args.folder[0])]
