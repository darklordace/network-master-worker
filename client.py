#!/usr/bin/env python3

import asyncio
import sys
import random

HOST = "127.0.0.1"                            # The server's hostname or IP address
PORT = 65432                                  # The port used by the server

long_list_length = int(input("Elements to send: "))
long_list_length = min(long_list_length, 25)  # Limit long list length to 25

if len(sys.argv) >= 2:
    HOST = sys.argv[1]

def generate_long_list():
    res = []
    for i in range(long_list_length):
        res.append(random.randint(-1000, 1000))
    return res

async def contact_master(message, host, port, id):
    message = str(message)
    reader, writer = await asyncio.open_connection(host, port)

    print(f'({id}) Send: {message!r}')
    writer.write(message.encode())
    await writer.drain() # Flow control

    data = ""
    while True:
        MAX_BYTES = 1024
        chunk = await reader.read(MAX_BYTES)
        data += chunk.decode()
        if len(chunk) < MAX_BYTES:
            break

    print(f'({id}) Received: {data}')
    print(f'({id}) Close the connection')
    writer.close()
    await writer.wait_closed()

    return data

for i in range(3):
    asyncio.run(contact_master(generate_long_list(), HOST, PORT, i))
