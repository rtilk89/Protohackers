import asyncio
import string

NAME_PROMPT = "Welcome to budgetchat! What shall I call you?\n"
CONNECTIONS = {}

LOCK = asyncio.Lock()

def is_valid_name(name, current_names):
    for letter in name:
        if letter not in string.ascii_uppercase + string.ascii_lowercase + string.digits:
            return False
        if name in current_names:
            return False
    return True


def format_message(name, message):
    return f"[{name}] {message}\n"


async def notify_new_user_entered(new_name, current_connections):
    notification = "* " + new_name + " has entered the room\n"
    print(notification)
    for name, writer in current_connections.items():
        writer.write(notification.encode())
        await writer.drain()


async def notify_user_left(name, current_connections):
    notification = "* " + name + " has left the room\n"
    print(notification)
    for client_name, writer in current_connections.items():
        try:
            writer.write(notification.encode())
            await writer.drain()
        except:
            print("Could not send user left message to " + client_name)


async def send_message_to_all_connections(name, message, current_connections):
    notification = format_message(name, message)
    print(notification)
    for client_name, writer in current_connections.items():
        if client_name == name:
            continue
        print("Writing message to " + client_name)
        writer.write(notification.encode())
        await writer.drain()


async def send_current_users_in_room(writer, current_connections):
    notification = "* The room contains: " + ", ".join(current_connections.keys()) + "\n"
    print(notification)
    writer.write(notification.encode())
    await writer.drain()


async def handle(reader, writer):
    global CONNECTIONS
    writer.write(NAME_PROMPT.encode())
    await writer.drain()
    name = await reader.readuntil(b"\n")
    name = name.decode("utf-8").strip()
    if not is_valid_name(name, CONNECTIONS.keys()):
        print("Not valid name")
        writer.close()
        return await writer.wait_closed()
    else:
        async with LOCK:
            await send_current_users_in_room(writer, CONNECTIONS)
            await notify_new_user_entered(name, CONNECTIONS)
            CONNECTIONS[name] = writer

    while True:
        try:
            message = await reader.readuntil(b"\n")
            message = message.decode("utf-8").strip()
            async with LOCK:
                await send_message_to_all_connections(name, message, CONNECTIONS)
        except Exception as e:
            print(e)
            break

    async with LOCK:
        CONNECTIONS.pop(name, None)
        await notify_user_left(name, CONNECTIONS)
    writer.close()


async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
