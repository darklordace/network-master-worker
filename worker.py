#!/usr/bin/env python3

import asyncio
import sys

HOST = "127.0.0.1"                                # Standard loopback interface address (localhost)
PORT = -1                                       # Port to listen on (non-privileged ports are > 1023)

if len(sys.argv) >= 3:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

if PORT == -1:
    PORT = int(input("PORT: "))

# Algorithm to compute Subset Sum Solutions using Brute Force
def cari_jawaban(data_list, pos, sum, ans):
    if pos == len(data_list):
        return 1 if (sum == 0 and len(ans) > 0) else 0
    ans.append(data_list[pos])
    result = cari_jawaban(data_list, pos + 1, sum + data_list[pos], ans)
    ans.pop()
    result += cari_jawaban(data_list, pos + 1, sum, ans)
    return result

async def worker_server(reader, writer):
    data = ""
    while True:
        MAX_BYTES = 1024
        chunk = await reader.read(MAX_BYTES)  # Max number of bytes to read
        data += chunk.decode()
        if len(chunk) < MAX_BYTES:
            break
    
    data_list = [int(x) for x in data.strip("][").split(", ")]
    ans = []
    data = str(cari_jawaban(data_list, 0, 0, ans))

    writer.write(data.encode())
    await writer.drain()  # Flow control
    writer.close()
    await writer.wait_closed()

async def main(host, port):
    server = await asyncio.start_server(worker_server, host, port)
    await server.serve_forever()

asyncio.run(main(HOST, PORT))
