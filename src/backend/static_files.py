import os

# ../../frontend/ from this file
STATIC_FILES_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__.encode())), b"frontend/"
)

file_contents: dict[bytes, bytes] = {}


def load():
    for root, _, files in os.walk(STATIC_FILES_ROOT):
        for filename in files:
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path):
                with open(full_path, "rb") as file:
                    relative_path = os.path.relpath(full_path, STATIC_FILES_ROOT)
                    file_contents[relative_path] = file.read()


def filename_to_response(filename: bytes) -> bytes:
    if filename == b"":
        filename = b"index.html"
    if filename not in file_contents:
        return b"HTTP/1.0 404\r\n\r\nNot found."

    response = b"HTTP/1.0 200\r\nContent-Type: "
    if filename.endswith(b".html"):
        response += b"text/html"
    elif filename.endswith(b".js"):
        response += b"application/javascript"
    elif filename.endswith(b".css"):
        response += b"text/css"
    elif filename.endswith(b".ico"):
        response += b"image/x-icon"
    else:
        response += b"text/plain"

    response += (
        "\r\n"
        f"Content-Length: {len(file_contents[filename])}\r\n"
        "Cache-Control: max-age=86400\r\n"
        "Connection: close\r\n\r\n"
    ).encode("utf-8")
    response += file_contents[filename]
    return response
