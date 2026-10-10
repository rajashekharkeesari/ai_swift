// API client for the SwiftVisa FastAPI backend.
// In dev, requests go through the Vite proxy (see vite.config.js).
// In production, set VITE_API_BASE_URL to the backend origin.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export async function screenVisa(query, k = 3) {
  const response = await fetch(`${API_BASE_URL}/screen`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, k }),
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      if (data?.detail) detail = data.detail;
    } catch {
      // response had no JSON body; keep the default message
    }
    throw new Error(detail);
  }

  return response.json();
}
