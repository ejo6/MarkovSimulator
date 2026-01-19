const form = document.getElementById("chain-form");
const output = document.getElementById("output");
const status = document.getElementById("status");
const chart = document.getElementById("chart");
const csvPath = "convergence.csv";

chart.addEventListener("error", () => {
  status.textContent = "Chart error";
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  status.textContent = "Running";

  const payload = {
    edges: JSON.parse(document.getElementById("edges").value),
    start: document.getElementById("start").value,
    iterations: Number(document.getElementById("iterations").value),
    burnIn: Number(document.getElementById("burnIn").value),
    write_interval: Number(document.getElementById("writeInterval").value)
  };

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    output.textContent = JSON.stringify(data, null, 2);
    status.textContent = response.ok ? "Success" : "Error";
    if (response.ok && payload.write_interval > 0) {
      chart.src = `/api/chart?csv_path=${encodeURIComponent(csvPath)}&t=${Date.now()}`;
    } else {
      chart.removeAttribute("src");
    }
  } catch (error) {
    output.textContent = JSON.stringify({ error: error.message }, null, 2);
    status.textContent = "Error";
    chart.removeAttribute("src");
  }
});
