#!/usr/bin/env python3

import asyncio
import os
import random

HOST = os.getenv("MASTER_HOST", "127.0.0.1")  # The server's hostname or IP address
PORT = 65432                                  # The port used by the server

def generate_long_list():
    res = []
    for i in range(25):
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
