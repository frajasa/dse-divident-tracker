import { authHeaders } from "./auth";

const BASE = "/api";

// ─── Public endpoints (no auth required) ─────────────────────────

export async function fetchDividends(year?: string) {
  const url = year ? `${BASE}/dividends/?year=${year}` : `${BASE}/dividends/`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchYields() {
  const res = await fetch(`${BASE}/dividends/yields`);
  return res.json();
}

export async function fetchUpcoming(days = 90) {
  const res = await fetch(`${BASE}/dividends/upcoming?days=${days}`);
  return res.json();
}

export async function fetchHistory(symbol: string) {
  const res = await fetch(`${BASE}/dividends/history/${symbol}`);
  return res.json();
}

export async function fetchCompanies() {
  const res = await fetch(`${BASE}/companies/`);
  return res.json();
}

export async function calculateTax(data: {
  shares: number;
  dividend_per_share: number;
  residency: string;
  investor_type: string;
  country?: string;
  purchase_price?: number;
}) {
  const res = await fetch(`${BASE}/tax/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function calculatePortfolioTax(data: {
  holdings: Array<{
    symbol: string;
    company_name: string;
    shares: number;
    dividend_per_share: number;
    purchase_price?: number;
  }>;
  residency: string;
  investor_type: string;
  country?: string;
}) {
  const res = await fetch(`${BASE}/tax/portfolio`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// ─── Auth endpoints ──────────────────────────────────────────────

export async function registerUser(phone: string, password: string, name: string) {
  const res = await fetch(`${BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, password, name }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Registration failed");
  }
  return res.json();
}

export async function loginUser(phone: string, password: string) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Login failed");
  }
  return res.json();
}

// ─── Protected endpoints (require auth) ──────────────────────────

export async function fetchPortfolio() {
  const res = await fetch(`${BASE}/portfolio/`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function addHolding(data: {
  symbol: string;
  shares: number;
  purchase_price?: number;
}) {
  const res = await fetch(`${BASE}/portfolio/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(data),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function removeHolding(holdingId: number) {
  const res = await fetch(`${BASE}/portfolio/${holdingId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function fetchProjections() {
  const res = await fetch(`${BASE}/portfolio/projections`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function fetchPortfolioPerformance() {
  const res = await fetch(`${BASE}/portfolio/performance`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function fetchPortfolioSummary() {
  const res = await fetch(`${BASE}/portfolio/summary`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

// ─── Analytics endpoints ─────────────────────────────────────────

export async function fetchMarketOverview() {
  const res = await fetch(`${BASE}/analytics/overview`);
  return res.json();
}

export async function fetchSectorAnalysis() {
  const res = await fetch(`${BASE}/analytics/sectors`);
  return res.json();
}

export async function fetchTopPayers(limit = 10) {
  const res = await fetch(`${BASE}/analytics/top-payers?limit=${limit}`);
  return res.json();
}

export async function fetchYieldTrends() {
  const res = await fetch(`${BASE}/analytics/yield-trends`);
  return res.json();
}

export async function fetchGrowthLeaders() {
  const res = await fetch(`${BASE}/analytics/growth-leaders`);
  return res.json();
}

export async function fetchDividendAristocrats() {
  const res = await fetch(`${BASE}/analytics/aristocrats`);
  return res.json();
}

export async function fetchMarketMovers() {
  const res = await fetch(`${BASE}/analytics/movers`);
  return res.json();
}

export async function fetchRiskMetrics() {
  const res = await fetch(`${BASE}/analytics/risk-metrics`);
  return res.json();
}

// ─── Education endpoints ─────────────────────────────────────────

export async function fetchEducationCategories() {
  const res = await fetch(`${BASE}/education/categories`);
  return res.json();
}

export async function fetchLesson(lessonId: string) {
  const res = await fetch(`${BASE}/education/lesson/${lessonId}`);
  return res.json();
}

export async function searchLessons(query: string) {
  const res = await fetch(`${BASE}/education/search?q=${encodeURIComponent(query)}`);
  return res.json();
}

// ─── Assistant endpoint ──────────────────────────────────────────

export async function askAssistant(question: string) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...authHeaders(),
  };
  const res = await fetch(`${BASE}/assistant/ask`, {
    method: "POST",
    headers,
    body: JSON.stringify({ question }),
  });
  return res.json();
}

// ─── Watchlist & Alerts endpoints ────────────────────────────────

export async function fetchWatchlist() {
  const res = await fetch(`${BASE}/watchlist/`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function addToWatchlist(symbol: string, notes?: string) {
  const res = await fetch(`${BASE}/watchlist/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ symbol, notes }),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function removeFromWatchlist(itemId: number) {
  const res = await fetch(`${BASE}/watchlist/${itemId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function fetchPriceAlerts() {
  const res = await fetch(`${BASE}/watchlist/price-alerts`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function createPriceAlert(data: {
  symbol: string;
  alert_type: string;
  target_value: number;
}) {
  const res = await fetch(`${BASE}/watchlist/price-alerts`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(data),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function deletePriceAlert(alertId: number) {
  const res = await fetch(`${BASE}/watchlist/price-alerts/${alertId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function fetchNotifications(unreadOnly = false) {
  const url = unreadOnly
    ? `${BASE}/watchlist/notifications?unread_only=true`
    : `${BASE}/watchlist/notifications`;
  const res = await fetch(url, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

// ─── Alert Preferences ──────────────────────────────────────────

export async function fetchAlertPreferences() {
  const res = await fetch(`${BASE}/alerts/preferences`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function createAlertPreference(data: {
  alert_type: string;
  channel: string;
  days_before: number;
  company_symbol?: string;
}) {
  const res = await fetch(`${BASE}/alerts/preferences`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(data),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function deleteAlertPreference(prefId: number) {
  const res = await fetch(`${BASE}/alerts/preferences/${prefId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}

export async function fetchUpcomingAlerts() {
  const res = await fetch(`${BASE}/alerts/upcoming`, {
    headers: authHeaders(),
  });
  if (res.status === 401) throw new Error("Unauthorized");
  return res.json();
}
