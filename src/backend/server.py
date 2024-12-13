#!/usr/bin/env python3
import asyncio
import base64
import logging
import socket
import ssl
import static_files
import time
from config import load_config, ServerConfig


class Server:
    def __init__(self, config: ServerConfig):
        self.config = config

    def handle_message(self, req_line: bytes) -> bytes:
        r"""
        Convert HTTP request-line into HTTP response.

        Support two kinds of request-lines:

        1. Front-end UI static resources, accessed from any modern web browser:
        - `GET /resource HTTP/1.1`

        2. User-generated response, can be accessed *not only* from web browsers
        (i.e. support HTTP/0.9 to HTTP/1.1 syntax, incl. absoluteURI):
        - `METHOD /data/<URL-safe base64>`
        - `METHOD /data/<URL-safe base64> <optional HTTP version>`
        - `METHOD https://domain.test/data/<URL-safe base64> <optional HTTP version>`
        Support at the same time:
        - subpaths e.g. `/data/<URL-safe base64>/what/ever`
        - query params, e.g. `/data/<URL-safe base64>?x=y`

        :param req_line: HTTP request-line, without any newlines or carriage returns in the end
        :return: Full HTTP response
        """
        # UI static resource
        if req_line.startswith(b"GET /") and not req_line.startswith(
            b"GET " + self.config.data_req_prefix
        ):
            idx = req_line.find(b" ", len(b"GET /"))
            if idx == -1:
                logging.debug(
                    "Invalid request: starts like a request for static resource (`GET /...`),"
                    "but doesn't contain space after start of request-URI. No HTTP/0.9 support for static resources."
                )
                return b""
            filename = req_line[len(b"GET /") : idx]
            logging.debug("Requested static file: %s", filename)
            return static_files.filename_to_response(filename)

        # User-generated response
        data_idx = req_line.find(self.config.data_req_prefix)
        if data_idx == -1:
            logging.debug(
                "Invalid request: neither static resource nor contains prefix for user-generated response"
            )
            return b""

        start_idx = data_idx + len(self.config.data_req_prefix)
        stop_idx = min(
            (
                idx
                for idx in (  # whichever comes first:
                    req_line.find(b" ", start_idx),  # request-URI end (HTTP/1.1)
                    req_line.find(b"/", start_idx),  # subpath start
                    req_line.find(b"?", start_idx),  # query param start
                )
                if idx != -1
            ),
            default=len(req_line),  # fall back to HTTP/0.9
        )

        logging.debug("Extracted base64: %s", req_line[start_idx:stop_idx])

        try:
            # Padding required by `urlsafe_b64decode` (unnecessary padding discarded)
            return base64.urlsafe_b64decode(req_line[start_idx:stop_idx] + b"==")
        except Exception:
            return b"HTTP/1.0 418\r\n\r\nInvalid base64."

    async def client_connected(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
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
            logging.debug("Connection from %s", writer.get_extra_info("peername"))

            data = b""
            try:
                data = await asyncio.wait_for(
                    reader.readline(), timeout=self.config.request_timeout
                )
                response: bytes = self.handle_message(data.strip(b"\n\r"))
            except asyncio.TimeoutError:
                response = b"HTTP/1.0 408\r\n\r\nRequest timed out."

            logging.debug("Request:")
            logging.debug(data)
            logging.debug("Response:")
            logging.debug(response)

            writer.write(response)
            await writer.drain()

            logging.debug("Closing connection")
            writer.close()
            await writer.wait_closed()
            logging.debug("Connection closed")
        except Exception as e:
            # Keep >= INFO level logs clean (catching ConnectionResetError, ssl.SSLError, TimeoutError, ...)
            logging.debug(e)

    async def start(self):
        ssl_context = None
        ssl_handshake_timeout = None
        ssl_shutdown_timeout = None
        if self.config.https_enabled:
            logging.debug("HTTPS enabled")
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(
                self.config.tls_cert_path, keyfile=self.config.tls_key_path
            )
            ssl_handshake_timeout = 10
            ssl_shutdown_timeout = 5

        try:
            server: asyncio.Server = await asyncio.start_server(
                client_connected_cb=self.client_connected,
                host=self.config.host,
                port=self.config.port,
                ssl=ssl_context,
                start_serving=False,  # start serving on serve_forever()
                limit=self.config.request_max_size,
                ssl_handshake_timeout=ssl_handshake_timeout,
                ssl_shutdown_timeout=ssl_shutdown_timeout,
                # backlog=100 max queued conn.-s by default
                # https://docs.python.org/3.13/library/asyncio-stream.html#asyncio.start_server
                # https://docs.python.org/3.13/library/asyncio-eventloop.html#asyncio.loop.create_server
            )
        except OSError as e:
            logging.error(f"Cannot start server: {e}")
            exit(1)

        for sock in server.sockets:
            host, port, *extra = sock.getsockname()
            ipv6 = sock.family == socket.AF_INET6
            scope_id = extra[1] if ipv6 else None

            url = (
                f"http{'s' if self.config.https_enabled else ''}://"
                f"{'[' if ipv6 else ''}{host}{f'%{scope_id}' if scope_id else ''}{']' if ipv6 else ''}:{port}/"
            )

            logging.info("Starting to serve on: %s", url)

        static_files.load()
        logging.debug(
            "Loaded static files into memory: %s",
            [k.decode("utf-8") for k in static_files.file_contents.keys()],
        )

        async with server:
            await server.serve_forever()


def main():
    config = load_config()

    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s (%(filename)s:%(lineno)d) %(levelname)-6s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    logging.Formatter.converter = time.gmtime  # UTC

    server = Server(config)
    try:
        asyncio.run(server.start(), debug=config.debug)
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt, exit.")


if __name__ == "__main__":
    main()
