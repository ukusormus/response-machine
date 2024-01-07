import argparse
import asyncio
import base64
import logging
import ssl

import static_files

REQ_MSG_PREFIX: bytes = b"GET /data/"
REQ_MSG_MAX_LEN: int = 8000


def handle_message(data: bytes) -> bytes:
    if data[:len(REQ_MSG_PREFIX)] != REQ_MSG_PREFIX:
        # Hacky static file serving
        # Only support `GET /<filename> HTTP/...`
        idx = data.find(b' ', len(b"GET /"))
        if idx == -1:
            return b"HTTP/1.0 418\r\n\r\nInvalid request."
        filename = data[len(b"GET /"):idx]
        return static_files.filename_to_response(filename)
    try:
        # Support both likes of `GET /data/eY HTTP/...` and
        # `GET /data/eY<EOF>` (HTTP 0.9) for the /data/ requests
        start = len(REQ_MSG_PREFIX)
        idx = data.find(b' ', start)
        stop = idx if idx != -1 else len(data)
        logging.debug(data[start:stop])
        return base64.urlsafe_b64decode(data[start:stop] + b"==")
        # ^ padding hack to support unpadded urlsafe base64 for the base64 library; any unnecessary padding is discarded
    except Exception:
        return b"HTTP/1.0 400\r\n\r\nInvalid base64."


async def client_connected(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data: bytes = await reader.read(REQ_MSG_MAX_LEN)

    response: bytes = handle_message(data)

    addr = writer.get_extra_info("peername")
    logging.debug(f"Received {data} from {addr}")

    logging.debug(f"Send: {response}")
    writer.write(response)
    await writer.drain()

    logging.debug("Close the connection")
    writer.close()
    await writer.wait_closed()


async def main(port: int, is_ssl: bool):
    static_files.load()
    logging.info(f"Loaded static files into memory: {list(static_files.file_contents.keys())}")

    ssl_context = None
    if is_ssl:
        logging.info("SSL")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_cert = "/etc/letsencrypt/live/response.ee/fullchain.pem"
        ssl_key = "/etc/letsencrypt/live/response.ee/privkey.pem"
        ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)

    server = await asyncio.start_server(
        client_connected_cb=client_connected,
        host='',  # '' = listen on all interfaces
        port=port,
        ssl=ssl_context
    )

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    logging.info(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port',
                        type=int, default=8888)
    parser.add_argument('--ssl', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    asyncio.run(main(port=args.port, is_ssl=args.ssl))
