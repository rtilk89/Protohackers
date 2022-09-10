import asyncio

async def echo(reader, writer):
    data = await reader.read(-1)
    addr = writer.get_extra_info("peername")

    print(f"Connection from {addr}")
    writer.write(data)
    await writer.drain()

    print("Closing the connection!")
    writer.close()


async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
