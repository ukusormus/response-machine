const unicodeEscSeqCheckbox = document.querySelector("input#unicode-esc-seq");
const manualNewlinesEscSeqCheckbox = document.querySelector("input#manual-newlines-esc-seq");
const syntaxHighlightingCheckbox = document.querySelector("input#syntax-highlighting");
// const exampleSelector = document.querySelector("input#example-select");
let hiddenTextarea;  // assigned in `onPageLoad()`

// \u[0] (\u[000000]) to \u[10FFFF]
const unicodeCodepointEscSeqRegex = new RegExp(
  /\\u\[(0*[0-9A-F]{1,5}|10[0-9A-F]{4})\]/, 'gi'
);

function isUnicodeEscSeqEnabled() {
  return unicodeEscSeqCheckbox.checked;
}

function isManualNewlinesEscSeqEnabled() {
  return manualNewlinesEscSeqCheckbox.checked;
}

function isSyntaxHighlightingEnabled() {
  return syntaxHighlightingCheckbox.checked;
}

function refreshHighlight() {
  hiddenTextarea.dispatchEvent(new Event("input"));
}

function loadExample(key) {
  hiddenTextarea.value = examples[key]["value"];
}

function highlight(codeElement) {
  // Custom highlighting:
  // innerHTML already HTML-encoded by code-input library
  let html = codeElement.innerHTML;
  const highlightMatch = match => `<kbd>${match}</kbd>`;

  if (isUnicodeEscSeqEnabled()) {
    html = html.replaceAll(
      unicodeCodepointEscSeqRegex,
      highlightMatch
    );
  }

  if (isManualNewlinesEscSeqEnabled()) {
    const newlinesRegex = /\\[rn]/g;
    html = html.replaceAll(newlinesRegex, highlightMatch);
  }

  codeElement.innerHTML = html;

  // highlight.js:
  if (isSyntaxHighlightingEnabled()) {
    codeElement.removeAttribute("data-highlighted");
    codeElement.removeAttribute("class");
    if (codeElement.innerText.substring(0, "http".length).toLowerCase() === "http") {
      // Force the first highlighting block as HTTP syntax to avoid flickering caused by language auto-detection
      codeElement.classList.add("language-http");
    }
    hljs.highlightElement(codeElement)
  }
}

function updateOutputLink() {
  const link = document.querySelector("a");
  let toBeEncoded = hiddenTextarea.value;


  if (isManualNewlinesEscSeqEnabled()) {
    // Remove visual newlines
    toBeEncoded = toBeEncoded.replaceAll(/[\n\r]/g, '');
    // Replace user input escape sequences
    toBeEncoded = toBeEncoded.replaceAll(/\\r/g, '\r').replaceAll(/\\n/g, '\n');
  } else {
    // Automatic newlines:
    // replace all user-visual newlines `\n` before the first `\n\n`, inclusive, with `\r\n`
    // (`\r\n` between HTTP headers, use `\n` in response body)
    toBeEncoded = toBeEncoded.replace(/([\s\S]*?\n\n)/, match => match.replace(/\n/g, '\r\n'));
  }

  if (isUnicodeEscSeqEnabled()) {
    toBeEncoded = toBeEncoded.replaceAll(
      unicodeCodepointEscSeqRegex,
      (_, codePoint) => String.fromCodePoint(parseInt(codePoint, 16))
    );
  }

  const output = `${location.origin}/data/${stringToURLSafeBase64(toBeEncoded)}`

  link.href = output;
  link.innerText = output;
}

function saveInputToURLFragment() {
  location.hash = new URLSearchParams({
    unicodeEscSeq: isUnicodeEscSeqEnabled(),
    manualNewlinesEscSeq: isManualNewlinesEscSeqEnabled(),
    syntaxHighlighting: isSyntaxHighlightingEnabled(),
    data: stringToURLSafeBase64(hiddenTextarea.value)
  }).toString();
}

function applyInputFromURLFragment() {
  const input = new URLSearchParams(location.hash.substring(1));

  if (input.has("unicodeEscSeq")) {
    unicodeEscSeqCheckbox.checked = input.get("unicodeEscSeq") === "true";
  }
  if (input.has("manualNewlinesEscSeq")) {
    manualNewlinesEscSeqCheckbox.checked = input.get("manualNewlinesEscSeq") === "true";
  }
  if (input.has("syntaxHighlighting")) {
    syntaxHighlightingCheckbox.checked = input.get("syntaxHighlighting") === "true";
  }
  if (input.has("data")) {
    try {
      const value = URLSafeBase64ToString(input.get("data"));
      hiddenTextarea.value = value;

      let customInput = true;
      for (const key in examples) {
        if (value === examples[key].value) {
          exampleSelector.value = key;
          customInput = false;
          break;
        }
      }
      if (customInput) {
        const option = createNewDropdownOption("custom", "(input from URL fragment)");
        exampleSelector.options.add(option);
        option.selected = true;
      }
    } catch (e) {
      hiddenTextarea.value = "";
    }
  }
}

// todo: examples

function update() {
  refreshHighlight();
  updateOutputLink();
  saveInputToURLFragment();
}

function onPageLoad() {
  codeInput.registerTemplate(
    "syntax-highlighted",
    new codeInput.Template(highlight, true, false, false, [])
  );

  [unicodeEscSeqCheckbox, manualNewlinesEscSeqCheckbox, syntaxHighlightingCheckbox]
    .forEach(el => el.addEventListener('change', refreshHighlight));

  [unicodeEscSeqCheckbox, manualNewlinesEscSeqCheckbox]
    .forEach(el => el.addEventListener('change', updateOutputLink));


  // Ignore HTML tags
  // (makes it easier to first apply our custom highlighting that creates html tags,
  // then highlight.js)
  hljs.addPlugin(mergeHTMLPlugin);
  hljs.configure({languages: ["http", "html", "javascript", "css"], ignoreUnescapedHTML: true});

  // Focus
  hiddenTextarea = document.querySelector("code-input > textarea");
  hiddenTextarea.focus();

  hiddenTextarea.addEventListener('change', updateOutputLink);

  [unicodeEscSeqCheckbox, manualNewlinesEscSeqCheckbox, syntaxHighlightingCheckbox,
    hiddenTextarea]
    .forEach(el => el.addEventListener('change', saveInputToURLFragment));
  // addEventListener("hashchange", applyInputFromURLFragment);

  // On page load: if there's URL fragment, try to apply it. Otherwise, load the default example
  if (location.hash) {
    applyInputFromURLFragment();
  } else {
    loadExample(DEFAULT_EXAMPLE_KEY);
  }

  update();
  // refreshHighlight();
  // updateOutputLink();
  // saveInputToURLFragment();

  exampleSelector.addEventListener("change", e => {
    if (exampleSelector.options.length > Object.keys(examples).length) {
      exampleSelector.options.remove(exampleSelector.options.length - 1);
    }

    loadExample(e.target.value);
    update();
  });
}

codeInput.runOnceWindowLoaded(onPageLoad, null);
