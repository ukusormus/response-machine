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
  "xss-alert": {
    "description": "XSS alert(1)",
    "value": `HTTP/1.1 200${CRLF}
Content-Type: text/html${CRLF}
${CRLF}
<script>alert(1)</script>`
  },
  "redirect-location": {
    "description": "Redirect (Location header)",
    "value": `HTTP/1.1 300${CRLF}
Location: https://www.example.org${CRLF}
${CRLF}`
  },
  "redirect-refresh": {
    "description": "Redirect (Refresh header)",
    "value": `HTTP/1.1 300${CRLF}
Refresh: 7; URL=https://www.example.com${CRLF}
${CRLF}
Redirecting in 7 seconds. See also: https://daniel.haxx.se/blog/2019/03/12/looking-for-the-refresh-header/`
  },
  "download-file": {
    "description": "Download file (Content-Disposition header)",
    "value": `HTTP/1.1 200${CRLF}
Content-Disposition: attachment; filename=ascii.txt; filename*=UTF-8''unic%C3%B6de.txt${CRLF}
${CRLF}
contentz`,
  },
  "go-crazy": {
    "description": "Invalid response?",
    "value": `HTTP/420\\r
x-wot: \\u0000test
\\n\\n\\n\\nbody?`
  },
};