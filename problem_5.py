import asyncio
import problem_3

UPSTREAM_HOST = "chat.protohackers.com"
UPSTREAM_PORT = 16963

TONYS_ADDRESS = "7YWHMfk9JZe0LM0g1ZauHuiSxhI"

def valid_address(address):
    return address.isalnum() and address.startswith("7") and 26 <= len(address) <= 35

async def proxy_messages(reader, writer):
    """Maliciously proxy messages between upstream and proxy"""
    while True:
        try:
            message = await reader.readuntil(b"\n")
            message = message.decode().strip()
            print(message)

            tokens = message.split(" ")
            if any(map(valid_address, tokens)):
                address_indexes = []
                for i, token in enumerate(tokens):
                    if valid_address(token):
                        address_indexes.append(i)
                if len(address_indexes) == 0:
                    raise ValueError("The algo is wrong")

                for idx in address_indexes:
                    tokens[idx] = TONYS_ADDRESS
                message = " ".join(tokens)

            message += "\n"
            writer.write(message.encode())
            await writer.drain()
        except Exception as e:
            print(e)
            break
    writer.write_eof()
    writer.close()
    await writer.wait_closed()


async def proxy_handler(proxy_reader, proxy_writer):
    # connect to upstream
    upstream_reader, upstream_writer = await asyncio.open_connection(UPSTREAM_HOST, UPSTREAM_PORT)
    asyncio.gather(proxy_messages(proxy_reader, upstream_writer), proxy_messages(upstream_reader, proxy_writer))


async def main():
    proxy = await asyncio.start_server(proxy_handler, "0.0.0.0", 8888)

    async with proxy:
        await proxy.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
