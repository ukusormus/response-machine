import {encode} from 'https://cdn.jsdelivr.net/npm/js-base64@3.7.5/base64.mjs';
import {examples} from "./examples.js";

const SERVER_URL = "http://localhost:8888/data/"

const root = document.querySelector("#root");
const httpResponseInput = document.querySelector("#httpResponse");
const responseLink = document.querySelector("#responseLink");
const errorMessage = document.querySelector("#errorMessage");
const exampleSelector = document.querySelector("#exampleSelect");

httpResponseInput.addEventListener("sl-input", () => {
  generateLink();
});

exampleSelector.addEventListener("sl-change", (e) => {
  loadExample(e.target.value);
  generateLink();
});


responseLink.innerText = responseLink.href = SERVER_URL;

// Avoid flash of undefined custom elements https://shoelace.style/getting-started/usage#waiting-for-components-to-load
await Promise.allSettled([
  customElements.whenDefined("sl-textarea"),
  customElements.whenDefined("sl-select"),
]);
root.classList.add("ready");
console.log("Ready to roll");

populateExamples();
loadExample("default")
generateLink();

/* ============ */

function loadExample(key) {
  httpResponseInput.value = examples[key]["value"];
}

function populateExamples() {
  for (const key in examples) {
    const option = document.createElement("sl-option");
    option.value = key;
    option.textContent = examples[key]["description"];
    exampleSelector.appendChild(option);
    option.selected = key === "default";
  }
}

/**
 * Generate the response URL from user's input and
 * display it to the user.
 */
function generateLink() {
  console.log(httpResponseInput.value)
  const text = transformInput(httpResponseInput.value);
  const link = `${SERVER_URL}${encode(text, true)}`;
  responseLink.href = link;
  responseLink.innerText = link;
}

/**
 * Remove newlines inserted by the browser and
 * transform user-inputted escape sequences.
 *
 * Show an error message if the transformation fails
 * (e.g. invalid Unicode sequence like `\uLOL` or
 * a single `\` where `\\` is meant).
 *
 * @param {String} input text from textarea
 * @returns {String} transformed input
 */
function transformInput(input) {
  let transformed = input.replace(/\n/g, '');

  try {
    transformed = eval('"' + transformed.replace(/"/g, '\\"') + '"')
    errorMessage.innerText = "";
  } catch (e) {
    errorMessage.innerText = "Error transforming string:\n" + e;
  }

  return transformed;
}
