async function checkHealth() {
  const statusEl = document.getElementById("health-status");
  if (!statusEl) return;

  try {
    const response = await fetch("/api/v1/health");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    statusEl.textContent = `API status: ${data.status}`;
    statusEl.className = "ok";
  } catch (error) {
    statusEl.textContent = "API unavailable";
    statusEl.className = "error";
    console.error(error);
  }
}

checkHealth();
