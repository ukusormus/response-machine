import os

STATIC_FILES_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__.encode())),
    b"frontend/")  # ../../frontend/ from this file

file_contents = {}


def load():
    for filename in os.listdir(STATIC_FILES_ROOT):
        full_path = os.path.join(STATIC_FILES_ROOT, filename)
        if os.path.isfile(full_path):
            with open(full_path, 'rb') as file:
                file_contents[filename] = file.read()


def filename_to_response(filename: bytes) -> bytes:
    if filename == b'':
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
    else:
        response += b"text/plain"

    response += b"\r\n\r\n" + file_contents[filename]
    return response
