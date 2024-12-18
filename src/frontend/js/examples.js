const exampleSelector = document.querySelector("select#example-select");
const DEFAULT_EXAMPLE_KEY = "minimal";
const examples = {
  "minimal": {
    "description": "Simple HTTP response, HTML body",
    "value": `HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<marquee><h1>hello \\u[1F30E]!`
  },
  "standard": {
    "description": "HTML5 body template",
    "value": `HTTP/1.1 200 OK
Content-Type: text/html

<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Title</title>
</head>
<body>

</body>
</html>`
  },
  "http-0.9": {
    "description": "HTTP/0.9",
    "value": `<HEADER>
<TITLE>The World Wide Web project</TITLE>
<NEXTID N="55">
</HEADER>
<BODY>
<H1>World Wide Web</H1>The WorldWideWeb (W3) is a wide-area<A
NAME=0 HREF="WhatIs.html">
hypermedia</A> information retrieval
initiative aiming to give universal
access to a large universe of documents.
[...]`
  },
  "invalid-http": {
    "description": "Invalid response?!",
    "value": `HTTP/420\\r
x-wot: \\u0000test
\\n\\n\\n\\n

firefox is fine with me, chromium ain't`
  },
  "content-length": {
    "description": "Content-Length playground",
    "value": `HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 080

what if longer than body? what if shorter than body?`
  },
  "xss-alert": {
    "description": "XSS alert(1)",
    "value": `HTTP/1.1 200
Content-Type: text/html

<script>alert(1)</script>`
  },
  "redirect-location": {
    "description": "Redirect (Location header)",
    "value": `HTTP/1.1 302
Location: https://www.example.com

`
  },
  "redirect-refresh": {
    "description": "Redirect (Refresh header)",
    "value": `HTTP/1.1 302
Refresh: 7; URL=https://www.example.com

<p>
Redirecting in 7 seconds.
<a href="https://daniel.haxx.se/blog/2019/03/12/looking-for-the-refresh-header/">Trivia from the creator of cURL</a>
</p>`
  },
  "redirect-meta-refresh": {
    "description": "Redirect (Refresh header in <meta>)",
    "value": `HTTP/1.1 200
Content-Type: text/html

<meta http-equiv="Refresh" content="7; URL=https://www.example.com"/>Redirecting in 7 seconds. `
  },
  "redirect-js": {
    "description": "Redirect (JavaScript)",
    "value": `HTTP/1.1 200
Content-Type: text/html

<script>location='//example.com'</script>`
  },
  "download-file": {
    "description": "Download file (Content-Disposition header)",
    "value": `HTTP/1.1 200
Content-Disposition: attachment; filename=ascii.txt; filename*=UTF-8''unic%C3%B6de.txt

contentz`,
  },
  "cookie": {
    "description": "Set-Cookie",
    "value": `HTTP/1.1 200
Set-Cookie: __Host-ID=123; Secure; Path=/; SameSite=Strict

`
  },
  "csp": {
    "description": "Content-Security-Policy",
    "value": `HTTP/1.1 200
Content-Security-Policy: default-src 'self'; style-src 'unsafe-inline'

<img src=x onerror=alert(1)>
<p style="color: red">red?</p>`
  },
  "www-authenticate": {
    "description": "WWW-Authenticate (Basic auth)",
    "value": `HTTP/1.1 401
WWW-Authenticate: Basic realm="test"

`
  },
  "xml-external-dtd": {
    "description": "XML External DTD",
    "value": `todo`
  }
};

function createNewDropdownOption(value, content) {
  const option = document.createElement("option");
  option.value = value;
  option.textContent = content;
  return option;
}

function populateExamples() {
  for (const key in examples) {
    const option = createNewDropdownOption(key, examples[key].description);
    exampleSelector.options.add(option);
    // option.selected = key === DEFAULT_EXAMPLE_KEY;
  }
}



populateExamples();