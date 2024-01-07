const CRLF = "\\r\\n"
export const examples = {
  "default": {
    "description": "Standard HTTP response, HTML body",
    "value": `HTTP/1.1 200 OK${CRLF}
Content-Type: text/html${CRLF}
Content-Length: 18${CRLF}
${CRLF}
<marquee><h1>hello`
  },
  "go-crazy": {
    "description": "Invalid response?!",
    "value": `HTTP/420\\r
x-wot: \\u0000test
\\n\\n\\n\\nfirefox likes me, chromium doesn't`
  },
  "xss-alert": {
    "description": "XSS alert(1)",
    "value": `HTTP/1.1 200${CRLF}
Content-Type: text/html${CRLF}
${CRLF}
<script>alert(1)</script>`
  },
  "redirect-location": {
    "description": "Redirect (Location header)",
    "value": `HTTP/1.1 302${CRLF}
Location: https://www.example.com${CRLF}
${CRLF}`
  },
  "redirect-refresh": {
    "description": "Redirect (Refresh header)",
    "value": `HTTP/1.1 302${CRLF}
Refresh: 7; URL=https://www.example.com${CRLF}
${CRLF}
Redirecting in 7 seconds. Trivia: https://daniel.haxx.se/blog/2019/03/12/looking-for-the-refresh-header/`
  },
  "redirect-meta-refresh": {
    "description": "Redirect (Refresh header in <meta>)",
    "value": `HTTP/1.1 200${CRLF}
Content-Type: text/html${CRLF}
${CRLF}
<meta http-equiv="Refresh" content="7; URL=https://www.example.com"/>Redirecting in 7 seconds. `
  },
  "redirect-js": {
    "description": "Redirect (JavaScript)",
    "value": `HTTP/1.1 200${CRLF}
Content-Type: text/html${CRLF}
${CRLF}
<script>location='//example.com'</script>`
  },
  "download-file": {
    "description": "Download file (Content-Disposition header)",
    "value": `HTTP/1.1 200${CRLF}
Content-Disposition: attachment; filename=ascii.txt; filename*=UTF-8''unic%C3%B6de.txt${CRLF}
${CRLF}
contentz`,
  },
  "cookie": {
    "description": "Set-Cookie",
    "value": `HTTP/1.1 200${CRLF}
Set-Cookie: __Host-ID=123; Secure; Path=/; SameSite=Strict${CRLF}
${CRLF}`
  },
  "csp": {
    "description": "Content-Security-Policy",
    "value": `HTTP/1.1 200${CRLF}
Content-Security-Policy: default-src 'self'; style-src 'unsafe-inline'${CRLF}
${CRLF}
<img src=x onerror=alert(1)>
<p style="color: red">red?</p>`
  },
  "www-authenticate": {
    "description": "WWW-Authenticate",
    "value": `HTTP/1.1 401${CRLF}
WWW-Authenticate: Basic realm="test"${CRLF}
${CRLF}`
  },
};