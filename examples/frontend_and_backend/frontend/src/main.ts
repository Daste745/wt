const apiUrl = import.meta.env.VITE_API_URL;

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
<section>
  <div>
    <h1>Frontend example</h1>

    <h2><code>VITE_API_URL=${apiUrl}</code></h2>

    <button id="test-button">Press</button>
    <p>
      <span>Backend response: </span>
      <span id="result"></span>
    </p>
  </div>
</section>
`;

function setupTestButton() {
  const testButton = document.querySelector<HTMLButtonElement>("#test-button")!;
  const resultSpan = document.querySelector<HTMLSpanElement>("#result")!;

  testButton.addEventListener("click", async () => {
    const response = await fetch(`${apiUrl}/`);
    resultSpan.textContent = await response.text();
  });
}

setupTestButton();
