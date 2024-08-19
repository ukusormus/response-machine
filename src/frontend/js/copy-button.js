const SHOW_FEEDBACK_TIME_MS = 500;

const copyButton = document.querySelector("button.copy-button");
const responseLink = document.querySelector("a#response-link");

copyButton.addEventListener("click", () => {
  copyTextToClipboard(responseLink.href);
});

function copyTextToClipboard(text) {
  if (!(navigator.clipboard && window.isSecureContext)) {
    fallbackCopyTextToClipboard(text);
    return;
  }
  navigator.clipboard.writeText(text).then(() => {
    showCopiedFeedback();
  }, (err) => {
    console.error('Async: Could not copy text: ', err);
  });
}

function showCopiedFeedback() {
  copyButton.classList.add('copied');
  setTimeout(() => {
    copyButton.classList.remove('copied');
  }, SHOW_FEEDBACK_TIME_MS);
}

function fallbackCopyTextToClipboard(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;

  // Avoid scrolling to bottom
  textArea.style.top = "0";
  textArea.style.left = "0";
  textArea.style.position = "fixed";

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    const successful = document.execCommand("copy");
    if (successful) {
      showCopiedFeedback();
    } else {
    console.error("Fallback: document.execCommand returned false, copying unsuccessful");
    }
  } catch (err) {
    console.error("Fallback: unable to copy", err);
  }

  document.body.removeChild(textArea);
}
