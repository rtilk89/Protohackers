import asyncio

class UDPHandler(asyncio.DatagramProtocol):
    def __init__(self):
        self.storage = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode("utf-8")

        equal_index = self._equal_index(message)
        if message.startswith("version") and equal_index < 0:
            # Special case for handling the version
            response = "version=Challenge 4 KeyValue Store".encode()
            self.transport.sendto(response, addr)
        elif equal_index > 0:
            key = message[:equal_index]
            value = message[equal_index+1:]
            self.storage[key] = value
        else:
            response = self._make_response(message)
            self.transport.sendto(response, addr)

    def _equal_index(self, data):
        return data.find("=")

    def _make_response(self, key):
        value = self.storage.get(key, "")
        return f"{key}={value}".encode()


async def main():
    print("Starting UDP server")

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPHandler(),
            local_addr=('0.0.0.0', 8888)
        )   

    try:
        await asyncio.sleep(3600)
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
