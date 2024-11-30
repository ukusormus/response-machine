FROM python:latest

COPY src/ /app/

WORKDIR /app/

EXPOSE 8888/tcp

CMD [ "python", "./backend/server.py", "-v" ]