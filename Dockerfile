FROM python:3.13-slim

WORKDIR /app
COPY src/ /app/

CMD [ "python", "./backend/server.py" ]