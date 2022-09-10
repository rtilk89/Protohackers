import asyncio
from dataclasses import dataclass
from statistics import mean, StatisticsError
from pprint import pprint

INSERT = "I"
QUERY = "Q"

@dataclass
class Message:
    nine_bytes: str

    @property
    def type(self):
        first_byte = self.nine_bytes[0]
        return chr(first_byte)

    @property
    def first_int(self):
        next_four_bytes = self.nine_bytes[1:5]
        return int.from_bytes(next_four_bytes, byteorder="big", signed=True)

    @property
    def second_int(self):
        last_four_bytes = self.nine_bytes[5:]
        return int.from_bytes(last_four_bytes, byteorder="big", signed=True)

    def __repr__(self):
        if self.type == INSERT:
            return f"<INSERT time:{self.first_int} price:{self.second_int}>"
        else:
            return f"<QUERY mintime:{self.first_int} maxtime:{self.second_int}>"


async def handle(reader, writer):
    local_storage = {}
    while True:
        try:
            data = await reader.readexactly(9)
        except asyncio.exceptions.IncompleteReadError:
            print("Incomplete read of 9 bytes. Disconnecting")
            break

        message = Message(data)
        print(message)

        if message.type == INSERT:
            timestamp = message.first_int
            price = message.second_int
            # if the price already exists don't replace it
            if timestamp in local_storage:
                continue
            local_storage[timestamp] = price
        elif message.type == QUERY:
            mintime = message.first_int
            maxtime = message.second_int
            try:
                _mean = mean(v for k, v in local_storage.items() if k >= mintime and k <= maxtime)
                _mean = round(_mean)
            except StatisticsError:
                _mean = 0
            try:
                output = _mean.to_bytes(4, byteorder="big", signed=True)
            except OverflowError:
                output = int(0).to_bytes(4, byteorder="big", signed=True)
            writer.write(output)
            await writer.drain()
        else:
            break

    writer.close()



async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
