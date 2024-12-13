FROM python:3.13-slim

WORKDIR /app
COPY src/ /app/

#EXPOSE 8888/tcp
#EXPOSE 8443/tcp

CMD [ "python", "./backend/server.py" ]