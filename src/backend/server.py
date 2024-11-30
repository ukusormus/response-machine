import argparse
import asyncio
import base64
import logging
import ssl

import static_files

logger = logging.getLogger(__name__)

REQ_TIMEOUT_SEC: int = 7
REQ_MAX_LEN: int = 5 * 1024 * 1024  # 5 MB
DATA_REQ_PREFIX = b"/data/"  # path to serve user-generated responses from


def handle_message(data: bytes) -> bytes:
    r"""
    Convert HTTP request into HTTP response.

    Support two kinds of request-lines:

    1. Front-end UI static resources, accessed from any modern web browser:
    - `GET /resource HTTP/1.1`

    2. User-generated response, may be accessed *not only* from web browsers:
    (support HTTP/0.9 to HTTP/1.1 syntax, incl. absoluteURI):
    - `METHOD /data/<URL-safe base64> <optional HTTP version>`
    - `METHOD https://response.ee/data/<URL-safe base64> <optional HTTP version>`

    :param data: HTTP request-line, without any newlines or carriage returns in the end
    :return: Full HTTP response
    """
    # UI static resource
    if data.startswith(b"GET /") and not data.startswith(b"GET " + DATA_REQ_PREFIX):
        idx = data.find(b" ", len(b"GET /"))
        if idx == -1:
            logger.debug("Invalid: `GET /x` (not `GET /x HTTP/1.1)")
            return b""
        filename = data[len(b"GET /") : idx]
        return static_files.filename_to_response(filename)

    # User-generated response
    data_idx = data.find(DATA_REQ_PREFIX)
    if data_idx == -1:
        logger.debug(
            "Invalid request: was not static resource, neither contains prefix for user-generated req"
        )
        return b""
    start_idx = data_idx + len(DATA_REQ_PREFIX)

    space_idx = data.find(b" ", start_idx)
    stop_idx = space_idx if space_idx != -1 else len(data)

    logger.debug("base64:")
    logger.debug(data[start_idx:stop_idx])

    try:
        # Padding required by `urlsafe_b64decode` (unnecessary padding discarded)
        return base64.urlsafe_b64decode(data[start_idx:stop_idx] + b"==")
    except Exception:
        return b"HTTP/1.0 418\r\n\r\nInvalid base64."


async def client_connected(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    r"""
    Handle client connection.

    Read data until whichever happens first:
    1. newline (`\n`) found
    2. EOF, i.e. client closes TCP connection (note, newline then not part of data)

    Serve response based on that data, and close connection.

    Error cases:
    3. too much data (over `limit` parameter in `asyncio.start_server`)
    4. timeout expires, waiting for client data

    :param reader: Where to read client request from
    :param writer: Where to write client response to
    :return: None
    """
    try:
        logger.debug(f"Connection from: {writer.get_extra_info('peername')}")

        data = b""
        try:
            data = await asyncio.wait_for(reader.readline(), timeout=REQ_TIMEOUT_SEC)
            response: bytes = handle_message(data.strip(b"\n\r"))
        except asyncio.TimeoutError:
            response = b"HTTP/1.0 408\r\n\r\nRequest timed out."

        logger.debug("Request:")
        logger.debug(data)
        logger.debug("Response:")
        logger.debug(response)

        writer.write(response)
        await writer.drain()

        logger.debug("Closing connection")
        writer.close()
        await writer.wait_closed()
        logger.debug("Connection closed")
    except Exception as e:
        # Keep logs clean (ConnectionResetError, ssl.SSLError, TimeoutError, ...)
        logger.debug(e)


def convert_sockname_to_url(address: tuple, is_ssl: bool):
    if ":" in address[0]:  # IPv6
        return f"http{'s' if is_ssl else ''}://[{address[0]}]:{address[1]}"
    else:  # IPv4
        return f"http{'s' if is_ssl else ''}://{address[0]}:{address[1]}"


async def main(port: int, is_ssl: bool):
    static_files.load()
    logger.debug(
        f"Loaded static files into memory: {[k.decode('utf-8') for k in static_files.file_contents.keys()]}"
    )

    ssl_context = None
    if is_ssl:
        logger.debug("SSL")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_cert = "/etc/letsencrypt/live/response.ee/fullchain.pem"
        ssl_key = "/etc/letsencrypt/live/response.ee/privkey.pem"
        ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)

    server = await asyncio.start_server(
        client_connected_cb=client_connected,
        host="",  # "" = listen on all interfaces
        port=port,
        ssl=ssl_context,
        limit=REQ_MAX_LEN,
    )

    logger.info(
        f"Serving on: {[convert_sockname_to_url(s.getsockname(), is_ssl) for s in server.sockets]}"
    )

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8888)
    parser.add_argument("--ssl", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    asyncio.run(main(port=args.port, is_ssl=args.ssl))
