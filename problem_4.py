import asyncio

STORAGE = {}

class UDPHandler(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode("utf-8")
        print(message)

        is_insert = self._is_insert(message)
        if message.startswith("version") and is_insert < 0:
            response = "version=Challenge 4 KeyValue Store".encode()
            self.transport.sendto(response, addr)
        elif message.startswith("version"):
            # don't update the version key
            pass
        elif is_insert > 0:
            print("IS INSERT")
            key = message[:is_insert]
            value = message[is_insert+1:]
            STORAGE[key] = value
        else:
            print("RETREIVE")
            response = self._make_response(message)
            self.transport.sendto(response, addr)

    def _is_insert(self, data):
        return data.find("=")

    def _make_response(self, key):
        value = STORAGE.get(key, "")
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
