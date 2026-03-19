"use client";

import { useEffect, useState } from "react";
import {
  fetchAlertPreferences,
  createAlertPreference,
  deleteAlertPreference,
  fetchUpcomingAlerts,
  fetchPriceAlerts,
  createPriceAlert,
  deletePriceAlert,
  fetchWatchlist,
  addToWatchlist,
  removeFromWatchlist,
} from "@/lib/api";
import { getToken } from "@/lib/auth";

type Tab = "watchlist" | "dividend-alerts" | "price-alerts";

const DSE_SYMBOLS = [
  "TBL", "NMB", "TCC", "TPCC", "CRDB", "SWIS", "DSE", "NICO",
  "TOL", "VODA", "AFRIPRISE", "DCB",
];

export default function AlertsPage() {
  const [tab, setTab] = useState<Tab>("watchlist");
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  // Watchlist state
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [watchSymbol, setWatchSymbol] = useState(DSE_SYMBOLS[0]);
  const [watchNotes, setWatchNotes] = useState("");

  // Dividend alert state
  const [alertPrefs, setAlertPrefs] = useState<any[]>([]);
  const [upcomingAlerts, setUpcomingAlerts] = useState<any[]>([]);
  const [newAlertType, setNewAlertType] = useState("pre_closure");
  const [newAlertChannel, setNewAlertChannel] = useState("whatsapp");
  const [newAlertDays, setNewAlertDays] = useState(7);
  const [newAlertSymbol, setNewAlertSymbol] = useState("");

  // Price alert state
  const [priceAlerts, setPriceAlerts] = useState<any[]>([]);
  const [priceAlertSymbol, setPriceAlertSymbol] = useState(DSE_SYMBOLS[0]);
  const [priceAlertType, setPriceAlertType] = useState("below");
  const [priceAlertTarget, setPriceAlertTarget] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = getToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }
    setAuthenticated(true);
    loadData();
  }, []);

  const asArray = (data: any) => (Array.isArray(data) ? data : []);

  const loadData = async () => {
    try {
      const [wl, prefs, upcoming, pAlerts] = await Promise.all([
        fetchWatchlist().catch(() => []),
        fetchAlertPreferences().catch(() => []),
        fetchUpcomingAlerts().catch(() => []),
        fetchPriceAlerts().catch(() => []),
      ]);
      setWatchlist(asArray(wl));
      setAlertPrefs(asArray(prefs));
      setUpcomingAlerts(asArray(upcoming));
      setPriceAlerts(asArray(pAlerts));
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  const handleAddToWatchlist = async () => {
    setError("");
    try {
      const result = await addToWatchlist(watchSymbol, watchNotes || undefined);
      if (result.detail) {
        setError(result.detail);
        return;
      }
      setWatchNotes("");
      const wl = await fetchWatchlist().catch(() => []);
      setWatchlist(asArray(wl));
    } catch (err: any) {
      setError(err.message || "Failed to add to watchlist. Please re-login.");
    }
  };

  const handleRemoveFromWatchlist = async (id: number) => {
    await removeFromWatchlist(id);
    const wl = await fetchWatchlist().catch(() => []);
    setWatchlist(asArray(wl));
  };

  const handleCreateAlertPref = async () => {
    await createAlertPreference({
      alert_type: newAlertType,
      channel: newAlertChannel,
      days_before: newAlertDays,
      company_symbol: newAlertSymbol || undefined,
    });
    const prefs = await fetchAlertPreferences().catch(() => []);
    setAlertPrefs(asArray(prefs));
  };

  const handleDeleteAlertPref = async (id: number) => {
    await deleteAlertPreference(id);
    const prefs = await fetchAlertPreferences().catch(() => []);
    setAlertPrefs(asArray(prefs));
  };

  const handleCreatePriceAlert = async () => {
    if (priceAlertTarget <= 0) return;
    await createPriceAlert({
      symbol: priceAlertSymbol,
      alert_type: priceAlertType,
      target_value: priceAlertTarget,
    });
    const pAlerts = await fetchPriceAlerts().catch(() => []);
    setPriceAlerts(asArray(pAlerts));
  };

  const handleDeletePriceAlert = async (id: number) => {
    await deletePriceAlert(id);
    const pAlerts = await fetchPriceAlerts().catch(() => []);
    setPriceAlerts(asArray(pAlerts));
  };

  if (authenticated === null || loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <div className="w-8 h-8 border-2 border-dse-blue border-t-transparent rounded-full animate-spin mb-3"></div>
        Loading...
      </div>
    );
  }

  const tabs: { id: Tab; label: string; count?: number }[] = [
    { id: "watchlist", label: "Watchlist", count: watchlist.length },
    { id: "dividend-alerts", label: "Dividend Alerts", count: alertPrefs.length },
    { id: "price-alerts", label: "Price Alerts", count: priceAlerts.length },
  ];

  return (
    <div>
      <h1 className="page-heading">Alerts & Watchlist</h1>
      <p className="page-subtitle mb-6">
        Track stocks, set price alerts, and get notified about dividend events.
      </p>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
              tab === t.id
                ? "bg-white text-dse-blue shadow-sm"
                : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
            }`}
          >
            {t.label}
            {t.count !== undefined && t.count > 0 && (
              <span
                className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${
                  tab === t.id ? "bg-dse-blue/10 text-dse-blue" : "bg-gray-200 text-gray-500"
                }`}
              >
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Watchlist Tab */}
      {tab === "watchlist" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card p-5 sm:p-6">
            <h2 className="font-semibold text-lg mb-4 text-gray-900">Add to Watchlist</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stock</label>
                <select
                  value={watchSymbol}
                  onChange={(e) => setWatchSymbol(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  {DSE_SYMBOLS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
                <input
                  type="text"
                  value={watchNotes}
                  onChange={(e) => setWatchNotes(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  placeholder="e.g., Watching for entry point"
                />
              </div>
              <button
                onClick={handleAddToWatchlist}
                className="w-full bg-dse-green text-white py-2.5 rounded-lg font-medium hover:bg-green-700 transition shadow-sm"
              >
                + Add to Watchlist
              </button>
            </div>
          </div>

          <div className="lg:col-span-2">
            {watchlist.length === 0 ? (
              <div className="card p-8 text-center">
                <div className="text-4xl text-gray-300 mb-3">&#128065;</div>
                <p className="text-gray-500 font-medium">Your watchlist is empty.</p>
                <p className="text-sm text-gray-400 mt-1">Add stocks to track them.</p>
              </div>
            ) : (
              <div className="card overflow-hidden">
                <div className="table-responsive">
                  <table className="w-full text-sm">
                    <thead className="bg-dse-blue text-white">
                      <tr>
                        <th className="px-4 py-3 text-left font-medium">Stock</th>
                        <th className="px-4 py-3 text-left font-medium hidden md:table-cell">Sector</th>
                        <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">Price</th>
                        <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">Dividend</th>
                        <th className="px-4 py-3 text-right font-medium">Yield</th>
                        <th className="px-4 py-3 text-left font-medium hidden lg:table-cell">Notes</th>
                        <th className="px-4 py-3 text-center font-medium">Remove</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {watchlist.map((w: any) => (
                        <tr key={w.id}>
                          <td className="px-4 py-3">
                            <div className="font-semibold text-gray-900">{w.symbol}</div>
                            <div className="text-xs text-gray-500">{w.name}</div>
                          </td>
                          <td className="px-4 py-3 text-gray-500 hidden md:table-cell">{w.sector}</td>
                          <td className="px-4 py-3 text-right font-mono hidden sm:table-cell">
                            {w.current_price ? `TZS ${Number(w.current_price).toLocaleString()}` : "—"}
                          </td>
                          <td className="px-4 py-3 text-right font-mono hidden sm:table-cell">
                            {w.latest_dividend ? `TZS ${Number(w.latest_dividend).toLocaleString()}` : "—"}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-700">
                              {w.dividend_yield}%
                            </span>
                          </td>
                          <td className="px-4 py-3 text-xs text-gray-400 hidden lg:table-cell">
                            {w.notes || "—"}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <button
                              onClick={() => handleRemoveFromWatchlist(w.id)}
                              className="text-red-400 hover:text-red-600 text-xs font-medium transition"
                            >
                              Remove
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Dividend Alerts Tab */}
      {tab === "dividend-alerts" && (
        <div>
          {/* Upcoming alerts */}
          {upcomingAlerts.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
              <h3 className="font-semibold text-amber-800 mb-2">
                Active Alerts ({upcomingAlerts.length})
              </h3>
              <div className="space-y-2">
                {upcomingAlerts.map((a: any, i: number) => (
                  <div key={i} className="bg-white rounded-lg border border-amber-200 p-3 flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-gray-900">{a.symbol}</span>
                      <span className="text-sm text-gray-500 ml-2">{a.company_name}</span>
                      <div className="text-xs text-amber-700 mt-1">
                        Books close: {a.books_closure_date} ({a.days_until} days)
                        — TZS {Number(a.dividend_per_share).toLocaleString()}/share
                      </div>
                    </div>
                    <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-lg font-medium">
                      via {a.channel}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="card p-5 sm:p-6">
              <h2 className="font-semibold text-lg mb-4 text-gray-900">Create Alert</h2>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Alert Type</label>
                  <select
                    value={newAlertType}
                    onChange={(e) => setNewAlertType(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="pre_closure">Pre-Books Closure</option>
                    <option value="declared">Dividend Declared</option>
                    <option value="payment">Payment Due</option>
                    <option value="yield_opportunity">Yield Opportunity</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Channel</label>
                  <select
                    value={newAlertChannel}
                    onChange={(e) => setNewAlertChannel(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="whatsapp">WhatsApp</option>
                    <option value="sms">SMS</option>
                    <option value="email">Email</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Days Before</label>
                  <input
                    type="number"
                    value={newAlertDays}
                    onChange={(e) => setNewAlertDays(Number(e.target.value))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    min={1}
                    max={90}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Stock (optional — blank = all)
                  </label>
                  <select
                    value={newAlertSymbol}
                    onChange={(e) => setNewAlertSymbol(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">All stocks</option>
                    {DSE_SYMBOLS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={handleCreateAlertPref}
                  className="w-full bg-dse-blue text-white py-2.5 rounded-lg font-medium hover:bg-blue-800 transition shadow-sm"
                >
                  Create Alert
                </button>
              </div>
            </div>

            <div className="lg:col-span-2">
              <h2 className="font-semibold text-lg mb-3 text-gray-900">Your Alert Preferences</h2>
              {alertPrefs.length === 0 ? (
                <div className="card p-8 text-center">
                  <div className="text-4xl text-gray-300 mb-3">&#128276;</div>
                  <p className="text-gray-500 font-medium">No alert preferences set.</p>
                  <p className="text-sm text-gray-400 mt-1">Create one to get notified.</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {alertPrefs.map((p: any) => (
                    <div key={p.id} className="card p-4 flex items-center justify-between hover:shadow-md transition-shadow">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-semibold capitalize text-gray-900">
                            {p.alert_type.replace("_", " ")}
                          </span>
                          {p.company_symbol && (
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-lg font-medium">
                              {p.company_symbol}
                            </span>
                          )}
                          <span
                            className={`text-xs px-2 py-0.5 rounded-lg font-medium ${
                              p.is_active
                                ? "bg-green-100 text-green-700"
                                : "bg-gray-100 text-gray-500"
                            }`}
                          >
                            {p.is_active ? "Active" : "Paused"}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {p.days_before} days before — via {p.channel}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteAlertPref(p.id)}
                        className="text-red-400 hover:text-red-600 text-xs font-medium transition"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Price Alerts Tab */}
      {tab === "price-alerts" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card p-5 sm:p-6">
            <h2 className="font-semibold text-lg mb-4 text-gray-900">Set Price Alert</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stock</label>
                <select
                  value={priceAlertSymbol}
                  onChange={(e) => setPriceAlertSymbol(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  {DSE_SYMBOLS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Alert When Price</label>
                <select
                  value={priceAlertType}
                  onChange={(e) => setPriceAlertType(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="below">Falls Below</option>
                  <option value="above">Rises Above</option>
                  <option value="yield_above">Yield Goes Above</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {priceAlertType === "yield_above" ? "Target Yield (%)" : "Target Price (TZS)"}
                </label>
                <input
                  type="number"
                  value={priceAlertTarget}
                  onChange={(e) => setPriceAlertTarget(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  min={0}
                  step={priceAlertType === "yield_above" ? 0.1 : 1}
                />
              </div>
              <button
                onClick={handleCreatePriceAlert}
                className="w-full bg-dse-green text-white py-2.5 rounded-lg font-medium hover:bg-green-700 transition shadow-sm"
              >
                Set Alert
              </button>
            </div>
          </div>

          <div className="lg:col-span-2">
            <h2 className="font-semibold text-lg mb-3 text-gray-900">Your Price Alerts</h2>
            {priceAlerts.length === 0 ? (
              <div className="card p-8 text-center">
                <div className="text-4xl text-gray-300 mb-3">&#128200;</div>
                <p className="text-gray-500 font-medium">No price alerts set.</p>
                <p className="text-sm text-gray-400 mt-1">Create one to monitor stock prices.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {priceAlerts.map((a: any) => (
                  <div
                    key={a.id}
                    className={`card p-4 flex items-center justify-between hover:shadow-md transition-shadow ${
                      a.is_triggered ? "border-l-4 border-green-500" : ""
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-semibold text-gray-900">{a.symbol}</span>
                        <span className="text-xs text-gray-400">{a.company_name}</span>
                        {a.is_triggered && (
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-lg font-medium">
                            Triggered
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        {a.alert_type === "below"
                          ? "Alert when price falls below"
                          : a.alert_type === "above"
                            ? "Alert when price rises above"
                            : "Alert when yield exceeds"}{" "}
                        <span className="font-mono font-semibold text-gray-700">
                          {a.alert_type === "yield_above"
                            ? `${a.target_value}%`
                            : `TZS ${Number(a.target_value).toLocaleString()}`}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeletePriceAlert(a.id)}
                      className="text-red-400 hover:text-red-600 text-xs font-medium transition"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
