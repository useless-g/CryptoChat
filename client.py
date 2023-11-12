#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import threading
from time import sleep

from DH import n_bit_random
from rsa.fast_pow_mod import fast_pow_mod
import RC6

thread_flag = True
nicks_private_keys = {}
DH_public_key = [0, 0]  # g, p
DH_private_key = [0, 0]  # a, g^a (mod p)


def read(sock):
    global symmetric_key
    while True:
        try:
            data = sock.recv(8192)
        except OSError:
            break
        try:
            data = data.decode()
            if data:
                if "###" in data:
                    alias, _, alias_private_DH_key = data.partition("###")  # nick, g^b (mod p)
                    nicks_private_keys[alias] = fast_pow_mod(int(alias_private_DH_key), DH_private_key[0], DH_public_key[1])
                    print(nicks_private_keys)
                else:
                    print()
                    print(data)
            else:
                break
        except UnicodeDecodeError:
            print('invalid characters')


def write(sock):
    global thread_flag

    my_alias = input('input your alias: ')  # Вводим наш псевдоним
    sock.send(f"{my_alias}@@@{DH_private_key[1]}".encode())

    print('To send message with old companion - input nickname and message text.')
    print("To make key exchange with new companion - input his nickname and empty message.")
    while thread_flag:
        sleep(1)
        try:
            addressee = input('Addressee: ').strip()
            message = input('Message: ').strip()

            if message:
                if nicks_private_keys.get(addressee):
                    data = f"[{my_alias}]: {message}"
                    # TODO: HERE WE NEED TO CIPHER DATA BEFORE SENDING
                    symmetric_key = nicks_private_keys[addressee]
                    RC6.encrypt(data, symmetric_key)

                    message_encoded = f"{addressee}$$${data}".encode()

                else:
                    print("First You have to make key exchange!")
                    continue
            else:  # key exchange
                message_encoded = f"{addressee}".encode()



            try:
                sock.send(message_encoded)
            except OSError:
                break

        except ValueError:
            break


def main():
    global thread_flag, DH_public_key, DH_private_key

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = 'localhost', 7777  # введите адрес и порт своего сервера

    # HERE WE NEED TO MAKE ASYMMETRIC KEYS

    try:
        sock.connect(server)
        data = sock.recv(8192)
        data = data.decode()
        DH_public_key[0], _, DH_public_key[1] = data.partition("@@@")
        DH_public_key = list(map(int, DH_public_key))
        DH_private_key[0] = n_bit_random(128)
        DH_private_key[1] = fast_pow_mod(DH_public_key[0], DH_private_key[0], DH_public_key[1])

    except ConnectionError:
        sys.exit("Connection refused")
    try:
        thread = threading.Thread(target=write, args=(sock, ))
        thread.start()
        read(sock)
        sock.close()
        thread_flag = False
        thread.join()
        sys.exit("\nServer dropped connection")
    except KeyboardInterrupt:
        sock.close()
        thread_flag = False
        exit('\nPress enter...')


if __name__ == '__main__':
    main()
