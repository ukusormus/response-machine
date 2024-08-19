function stringToURLSafeBase64(jsString) {
  const bytes = new TextEncoder().encode(jsString);
  const binString = Array.from(bytes, (byte) =>
    String.fromCodePoint(byte),
  ).join('');
  const base64 = btoa(binString);
  const urlSafeBase64 = base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  return urlSafeBase64;
}

function URLSafeBase64ToString(urlSafeBase64String) {
  const base64 = urlSafeBase64String.replace(/-/g, '+').replace(/_/g, '/');
  const binString = atob(base64);
  const bytes = Uint8Array.from(binString, m => m.codePointAt(0));
  const jsString = new TextDecoder().decode(bytes)
  return jsString;
}