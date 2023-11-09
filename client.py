#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import threading
from time import sleep

thread_flag = True


def read(sock):
    while True:
        try:
            data = sock.recv(8192)
        except OSError:
            break
        try:
            if data.decode('utf-8'):
                print()
                print(data.decode('utf-8'))
            else:
                break
        except UnicodeDecodeError:
            print('invalid characters')


def write(sock):
    global thread_flag

    alias = input('input your alias: ')  # Вводим наш псевдоним
    sock.send(alias.encode('utf-8'))

    print('To send message - input nickname and message text')
    while thread_flag:
        sleep(1)
        try:
            addressee = input('Addressee: ')
            message = input('Message: ')
            data = f"[{alias}]: {message}"

        # HERE WE nEED TO CIPHER DATA BEFORE SENDING

        except ValueError:
            break
        try:
            message_encoded = f"{addressee}$$${data}".encode('utf-8')
        except UnicodeEncodeError:
            print('invalid characters')
        else:
            try:
                sock.send(message_encoded)
            except OSError:
                break


def main():
    global thread_flag
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = 'localhost', 7777  # введите адрес и порт своего сервера
    try:
        sock.connect(server)
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
