#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
# import syslog
import asyncio
from collections import deque

connections = dict()  # (ip, port) : client socket
aliases = dict()  # alias : ip, port
addresses = dict()


async def connect(server_sock):
    while True:
        try:
            client, address = server_sock.accept()
        except BlockingIOError:
            await asyncio.sleep(0.5)
        else:
            print(':'.join(map(str, address)), 'connected')
            if address not in connections:
                client.setblocking(False)
                connections[address] = client  # добавляем клиента в словарь соединений


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
            else:
                client = connections[address]
                break
        else:
            await asyncio.sleep(1)
            continue

        if message:
            message_decoded = message.decode('utf-8')

            if address not in aliases.values():
                alias = message_decoded
                aliases[alias] = address
                addresses[address] = alias
                continue

            try:  # валидация ip и порта

                # логирование сообщений в syslog
                # syslog.syslog(syslog.LOG_NOTICE,
                #               f'from: {address[0]}:{address[1]}  to: {ip}:{port}  message: {data}'.strip())

                addressee, _, data = message_decoded.partition('$$$')
                addressee_socket = connections[aliases[addressee]]

                print(f'from: {addresses[address]} ({address[0]}:{address[1]})")\n'
                      f'to: {addressee} ({aliases[addressee]})\n'
                      f'message: {data}\n')

            except (ValueError, KeyError):
                try:
                    client.send("Message not delivered :'( \nNo such user".encode('utf-8'))
                except ConnectionError:
                    print(':'.join(map(str, address)), 'disconnected')
                    client.close()  # отсоединить клиента
                    alias = addresses[address]
                    del connections[address]
                    del addresses[address]
                    del aliases[alias]
            else:  # ip address in message is ok
                if address in connections:
                    try:
                        addressee_socket.send(data.encode('utf-8'))
                        client.send('Message delivered :) '.encode('utf-8'))
                    except ConnectionError:
                        client.send("Message not delivered :'( ".encode('utf-8'))
                else:
                    client.send("Message not delivered :'( \nNo such user".encode('utf-8'))

        else:  # empty message
            print(':'.join(map(str, address)), 'disconnected')
            client.close()
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
