#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import threading
from time import sleep

from DH.DH import n_bit_random
from rsa.fast_pow_mod import fast_pow_mod
from RC6 import RC6
from sha256.SHA import SHA
from rsa.cipher import RSA

thread_flag = True
nicks_private_keys = {}  # {bob: g^ab (mod p), alice: g^ac (mod p) ... }
DH_public_key = [0, 0]  # g, p
DH_private_key = [0, 0]  # a, g^a (mod p)
cipher = RC6.RC6()
hash_ = SHA()
RSA_cipher = RSA(cipher_key="private")
rsa_public_key, rsa_private_key = RSA_cipher.public_key, RSA_cipher.private_key
rsa_deciphers = {}


def read(sock):
    # global symmetric_key
    while True:
        try:
            data = sock.recv(8192)
        except OSError:
            break
        try:
            data = data.decode()
            print(data)
            if data:
                if "###" in data:
                    alias, alias_private_DH_key, alias_rsa_public_key0, alias_rsa_public_key1 = data.split("###")  # nick, g^b (mod p), rsa pub
                    nicks_private_keys[alias] = fast_pow_mod(int(alias_private_DH_key),
                                                             DH_private_key[0],
                                                             DH_public_key[1])
                    nicks_private_keys[alias] = nicks_private_keys[alias].to_bytes(length=16, byteorder="big")
                    rsa_deciphers[alias] = RSA(cipher_key="private", key=(int(alias_rsa_public_key0),
                                                                          int(alias_rsa_public_key1)))
                    print(nicks_private_keys)
                else:
                    pass
                    # print(39)
                    # TODO: WTF this state is?
                    # symmetric_key = nicks_private_keys[alias]
                    # data = cipher.decrypt(data, symmetric_key)
                    # print(data)
            else:
                break
        except UnicodeDecodeError:

            # TODO: HERE WE NEED TO DECIPHER DATA BEFORE PRINTING
            symmetric_key = nicks_private_keys[alias]
            data = cipher.decrypt(data, symmetric_key)
            for i in range(1, 257):
                if data[-i] != 0:
                    i -= 1
                    break

            fingerprint = rsa_deciphers[alias].decipher(bytes(data[-256-i:-i]))
            if hash_.hash(data[:-256-i]).to_bytes(length=32, byteorder="big") == fingerprint:
                print(bytes(data[:-256-i]).decode())
            else:
                print(hash_.hash(bytearray(data)))
                print(fingerprint)


def write(sock):
    global thread_flag

    my_alias = input('input your alias: ')  # Вводим наш псевдоним
    sock.send(f"{my_alias}@@@{DH_private_key[1]}@@@{rsa_public_key[0]}@@@{rsa_public_key[1]}".encode())

    print("To send message with old companion - input nickname and message text.")
    print("To make key exchange with new companion - input his nickname and empty message.")
    while thread_flag:
        sleep(1)
        try:
            addressee = input('Addressee: ').strip()
            message = input('Message: ').strip()

            if message:
                if nicks_private_keys.get(addressee):
                    data = f"[{my_alias}]: {message}"

                    b = bytearray(data.encode())
                    b = hash_.hash(b).to_bytes(length=32, byteorder="big")
                    print("hash =", b)
                    b = RSA_cipher.cipher(b)
                    # print(len(b))
                    print("rsa ciphered hash =", b)

                    # TODO: HERE WE NEED TO CIPHER DATA BEFORE SENDING
                    symmetric_key = nicks_private_keys[addressee]
                    data = cipher.encrypt(data.encode() + b, symmetric_key)
                    print("data before sending =", data)

                    # TODO: не надо шифровать алиас, так не получится у получателя понять какой нужен ключ
                    message_encoded = f"{addressee}$$$".encode() + data
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

    # TODO: HERE WE NEED TO MAKE ASYMMETRIC KEYS

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
