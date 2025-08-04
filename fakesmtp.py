import asyncio
import random

REPLIES = {
    'success': ["250 OK", "354 Start mail input; end with <CRLF>.<CRLF>"],
    'temporary': ["421 Service not available, closing transmission channel", "451 Requested action aborted"],
    'permanent': ["550 Requested action not taken", "553 Mailbox name not allowed"]
}

BANNERS = [
    b"220 smtp-FDLE ESMTP Service Ready\r\n",
    b"220 mx1.mail.local ESMTP\r\n",
    b"220 mail.server.example.com Simple Mail Transfer Service Ready\r\n"
]

def random_response():
    choice = random.choices(
        ['success', 'temporary', 'permanent'],
        weights=[0.7, 0.2, 0.1]
    )[0]
    return random.choice(REPLIES[choice])

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[+] Connection from {addr}")

    banner = random.choice(BANNERS)
    writer.write(banner)
    await writer.drain()

    while True:
        data = await reader.readline()
        if not data:
            break

        await asyncio.sleep(random.uniform(0.1, 1.5))  # Simulate latency
        command = data.decode().strip()
        print(f"[>] {addr}: {command}")

        if command.upper() == "QUIT":
            writer.write(b"221 Bye\r\n")
            await writer.drain()
            break
        elif command.upper().startswith("HELO") or command.upper().startswith("EHLO"):
            writer.write(f"250 {addr[0]} greets you\r\n".encode())
        elif command.upper().startswith("MAIL FROM"):
            writer.write(b"250 Sender OK\r\n")
        elif command.upper().startswith("RCPT TO"):
            writer.write(b"250 Recipient OK\r\n")
        elif command.upper() == "DATA":
            writer.write(b"354 End data with <CR><LF>.<CR><LF>\r\n")
            await writer.drain()
            # Simulate accepting message data
            while True:
                line = await reader.readline()
                if line.strip() == b".":
                    break
            writer.write(b"250 OK: queued as FAKE12345\r\n")
        else:
            response = random_response()
            writer.write((response + "\r\n").encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    print(f"[-] Connection closed: {addr}")

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 25)
    addr = server.sockets[0].getsockname()
    print(f"[+] Listening on {addr}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Shutting down")
