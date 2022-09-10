import asyncio
import json

from sympy import simplify

def is_valid_message(json_message):
    method = json_message.get("method")
    number = json_message.get("number")
    
    if method != "isPrime":
        return False
    if isinstance(number, bool):
        return False
    if not isinstance(number, (int, float)):
        return False
    return True

async def handle(reader, writer):
    while True:
        data = await reader.readuntil(b"\n")
        print(data)
        try:
            message = json.loads(data.decode("utf-8").strip())
            print(message)
        except:
            break

        if is_valid_message(message):
            output = {"method": "isPrime"}
            number = message['number']
            if isinstance(number, int) and simplify(number).is_prime:
                output["prime"] = True
            else:
                output["prime"] = False
            output = (json.dumps(output) + "\n").encode()
            writer.write(output)
            await writer.drain()
        else:
            writer.write(data)
            await writer.drain()
            break

    print("closing connection")
    writer.close()


async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
