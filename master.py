#!/usr/bin/env python3

import asyncio
import os
import sys
from collections import deque

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

if len(sys.argv) >= 2:
    HOST = sys.argv[1]

lock = asyncio.Lock()
queue = deque()
WORKER_LIST = [
    {
        "host": os.getenv("WORKER_1_HOST", "127.0.0.1"),
        "port": 65430,
        "conn": 0
    },
    {
        "host": os.getenv("WORKER_2_HOST", "127.0.0.1"),
        "port": 65425,
        "conn": 0
    },
    {
        "host": os.getenv("WORKER_3_HOST", "127.0.0.1"),
        "port": 65420,
        "conn": 0
    }
]

async def contact_worker(message, host, port):
    message = str(message)
    reader, writer = await asyncio.open_connection(host, port)

    writer.write(message.encode())
    await writer.drain() # Flow control

    data = ""
    while True:
        MAX_BYTES = 1024
        chunk = await reader.read(MAX_BYTES)
        data += chunk.decode()
        if len(chunk) < MAX_BYTES:
            break

    writer.close()
    await writer.wait_closed()

    return data

async def master_server(reader, writer):
    data = ""
    chosen_worker = None

    while True:
        MAX_BYTES = 1024
        chunk = await reader.read(MAX_BYTES)  # Max number of bytes to read
        data += chunk.decode()
        if len(chunk) < MAX_BYTES:
            break
    
    async with lock:
        queue.append(data)
    
    while True:
        async with lock:
            if queue[0] == data:
                for worker in WORKER_LIST:
                    if worker["conn"] == 0:
                        worker["conn"] += 1
                        queue.popleft()
                        chosen_worker = worker
                        break
        if chosen_worker:
            break
        await asyncio.sleep(1) # check queue every 1 second

    print(WORKER_LIST)
    port_chosen = chosen_worker["port"]
    mes = "Job handled at %s" % port_chosen
    print(mes)

    processed_data = await contact_worker(data, chosen_worker["host"], chosen_worker["port"])
    chosen_worker["conn"] -= 1

    notice = "Your job is done by port %s and the result is %s" % (port_chosen, processed_data)
    writer.write(notice.encode())
    await writer.drain()  # Flow control
    writer.close()
    await writer.wait_closed()

async def main(host, port):
    server = await asyncio.start_server(master_server, host, port)
    await server.serve_forever()

asyncio.run(main(HOST, PORT))
