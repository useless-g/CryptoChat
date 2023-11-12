#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import asyncio
from collections import deque
from time import time

from DH import gen_g_p

connections = {}  # (ip, port) : client socket
aliases = {}  # alias : ip, port
keys_by_alias = {}  # part of key for every alias
addresses = {}
t = time()
g, p = gen_g_p()  # DH public keys
print(g, p)
print(time() - t, "g, p generated.")


async def connect(server_sock):
    while True:
        try:
            client_socket, address = server_sock.accept()
        except BlockingIOError:
            await asyncio.sleep(0.5)
        else:
            print(':'.join(map(str, address)), 'connected')
            if address not in connections:
                client_socket.setblocking(False)
                connections[address] = client_socket  # добавляем клиента в словарь соединений
                client_socket.send(f"{g}@@@{p}".encode("utf-8"))  # send public DH keys


async def receive_and_send():
    while True:
        for address in connections:  # check all connections for messages else async sleep
            try:
                message = connections[address].recv(8192)  # принять 8 кб с клиента / ожидание сообщения nonblocking
            except BlockingIOError:
                await asyncio.sleep(0.001)
            except OSError:
                print(':'.join(map(str, address)), 'disconnected')
                connections[address].close()  # отсоединить клиента
                alias = addresses[address]
                del connections[address]
                del addresses[address]
                del aliases[alias]
                del keys_by_alias[alias]
            else:
                client_socket = connections[address]
                break
        else:
            await asyncio.sleep(1)
            continue

        if message:
            message_decoded = message.decode('utf-8')

            if address not in aliases.values():  # registration
                alias, _, private_key_part = message_decoded.partition("@@@")
                print(message_decoded)
                aliases[alias] = address
                addresses[address] = alias
                keys_by_alias[alias] = int(private_key_part)
                continue
            if message_decoded in aliases:  # key exchange
                try:
                    client_socket.send(f"{message_decoded}###{keys_by_alias[message_decoded]}".encode())
                    connections[aliases[message_decoded]].send(f"{addresses[address]}###{keys_by_alias[addresses[address]]}".encode())
                except (ValueError, KeyError):
                    client_socket.send("Message not delivered :'( \nNo such user".encode('utf-8'))
                except (ConnectionError, OSError):
                    print(':'.join(map(str, address)), 'disconnected')
                    connections[address].close()  # отсоединить клиента
                    alias = addresses[address]
                    del connections[address]
                    del addresses[address]
                    del aliases[alias]
                    del keys_by_alias[alias]
                continue

            try:  # валидация ip и порта
                addressee, _, data = message_decoded.partition('$$$')
                addressee_socket = connections[aliases[addressee]]

                print(f'from: {addresses[address]} ({address[0]}:{address[1]})")\n'
                      f'to: {addressee} ({aliases[addressee]})\n'
                      f'message: {data}\n')

            except (ValueError, KeyError):
                try:
                    client_socket.send("Message not delivered :'( \nNo such user".encode('utf-8'))
                except ConnectionError:
                    print(':'.join(map(str, address)), 'disconnected')
                    client_socket.close()  # отсоединить клиента
                    alias = addresses[address]
                    del connections[address]
                    del addresses[address]
                    del aliases[alias]
                    del keys_by_alias[alias]
            else:  # ip address in message is ok
                if address in connections:
                    try:
                        addressee_socket.send(data.encode('utf-8'))
                        client_socket.send('Message delivered :) '.encode('utf-8'))
                    except ConnectionError:
                        client_socket.send("Message not delivered :'( ".encode('utf-8'))
                else:
                    client_socket.send("Message not delivered :'( \nNo such user".encode('utf-8'))

        else:  # empty message
            print(':'.join(map(str, address)), 'disconnected')
            client_socket.close()
            del connections[address]


async def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setblocking(False)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', 7777))
    server_sock.listen()
    tasks = deque()

    tasks.append(asyncio.create_task(connect(server_sock)))
    tasks.append(asyncio.create_task(receive_and_send()))

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        pass
    finally:
        for item in connections.values():
            item.close()
        server_sock.close()


if __name__ == '__main__':
    print(socket.gethostname(), 'started working...')
    asyncio.run(main())
    print(socket.gethostname(), 'stopped working...')
