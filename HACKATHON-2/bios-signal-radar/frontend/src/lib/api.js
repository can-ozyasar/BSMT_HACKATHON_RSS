// Override with `VITE_API_URL` (e.g. "http://localhost:8000/api/v1")
export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch (e) {
    throw new Error(`Failed to fetch: ${url}`);
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const detail = errorData.detail;
    let message;
    if (typeof detail === 'string') {
      message = detail;
    } else if (detail?.message) {
      message = detail.message;
    } else if (detail?.error === 'rss_duplicate') {
      message = 'Bu RSS kaynağı zaten eklenmiş.';
    } else if (detail?.error === 'invalid_rss') {
      message = detail.message || 'Geçersiz RSS bağlantısı. Lütfen URL\'yi kontrol edin.';
    } else {
      message = errorData.error || `Sunucu hatası (${response.status}). Lütfen tekrar deneyin.`;
    }
    throw new Error(message);
  }

  return response.json();
}
