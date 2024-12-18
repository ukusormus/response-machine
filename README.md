# HTTP Response Machine 🤖

Raw HTTP response to URL converter

Demo: [https://response.ee](https://response.ee)\
(http:// also supported, wildcard subdomains supported (e.g. [http://x.y.z.response.ee](http://x.y.z.response.ee)), wildcard TLS soon™)

## Running Locally

### Without Docker

Run HTTP server (default):
```sh
python3 src/backend/server.py
```

Run HTTPS server:
```sh
python3 src/backend/server.py
```

### With Docker Compose

Run both HTTP and HTTPS servers:
```sh
docker compose up
```

Run only HTTP server:
```sh
docker compose up http
```

Run only HTTPS server:
```sh
docker compose up https
```

### Environment Variables

- `PORT` - Server port (default: 8888)
...
