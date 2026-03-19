"use client";

import { useEffect, useState } from "react";
import {
  fetchMarketOverview,
  fetchSectorAnalysis,
  fetchTopPayers,
  fetchDividendAristocrats,
  fetchMarketMovers,
  fetchRiskMetrics,
} from "@/lib/api";

type Tab = "overview" | "sectors" | "aristocrats" | "movers" | "risk";

export default function AnalyticsPage() {
  const [tab, setTab] = useState<Tab>("overview");
  const [overview, setOverview] = useState<any>(null);
  const [sectors, setSectors] = useState<any[]>([]);
  const [topPayers, setTopPayers] = useState<any[]>([]);
  const [aristocrats, setAristocrats] = useState<any[]>([]);
  const [movers, setMovers] = useState<any>(null);
  const [riskMetrics, setRiskMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const asArr = (d: any) => (Array.isArray(d) ? d : []);
    Promise.all([
      fetchMarketOverview().catch(() => null),
      fetchSectorAnalysis().catch(() => []),
      fetchTopPayers(10).catch(() => []),
      fetchDividendAristocrats().catch(() => []),
      fetchMarketMovers().catch(() => null),
      fetchRiskMetrics().catch(() => []),
    ]).then(([ov, sec, pay, ari, mov, risk]) => {
      setOverview(ov);
      setSectors(asArr(sec));
      setTopPayers(asArr(pay));
      setAristocrats(asArr(ari));
      setMovers(mov);
      setRiskMetrics(asArr(risk));
      setLoading(false);
    });
  }, []);

  const tabs: { id: Tab; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "sectors", label: "Sectors" },
    { id: "aristocrats", label: "Aristocrats" },
    { id: "movers", label: "Movers" },
    { id: "risk", label: "Risk Scores" },
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <div className="w-8 h-8 border-2 border-dse-blue border-t-transparent rounded-full animate-spin mb-3"></div>
        Loading market analytics...
      </div>
    );
  }

  return (
    <div>
      <h1 className="page-heading">Market Analytics</h1>
      <p className="page-subtitle mb-6">
        Deep insights into DSE dividend performance, sector analysis, and risk
        metrics.
      </p>

      {/* Tab Navigation */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              tab === t.id
                ? "bg-white text-dse-blue shadow-sm"
                : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Market Overview Tab */}
      {tab === "overview" && overview && (
        <div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard
              label="Listed Companies"
              value={overview.total_companies}
              color="blue"
            />
            <StatCard
              label="Paying Dividends"
              value={overview.companies_paying_dividends}
              color="green"
            />
            <StatCard
              label="Average Yield"
              value={`${overview.average_yield}%`}
              color="purple"
            />
            <StatCard
              label="Market Cap"
              value={`TZS ${Number(overview.total_market_cap).toLocaleString()}`}
              color="gold"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            <div className="card p-5 text-center border-l-4 border-green-500">
              <div className="text-3xl font-bold text-green-700">
                {overview.dividend_increased}
              </div>
              <div className="text-sm text-green-600 mt-1 font-medium">
                Increased Dividends
              </div>
            </div>
            <div className="card p-5 text-center border-l-4 border-red-400">
              <div className="text-3xl font-bold text-red-700">
                {overview.dividend_decreased}
              </div>
              <div className="text-sm text-red-600 mt-1 font-medium">
                Decreased Dividends
              </div>
            </div>
            <div className="card p-5 text-center border-l-4 border-gray-400">
              <div className="text-3xl font-bold text-gray-700">
                {overview.dividend_unchanged}
              </div>
              <div className="text-sm text-gray-500 mt-1 font-medium">Unchanged</div>
            </div>
          </div>

          {/* Top Payers */}
          <h2 className="text-xl font-bold mb-4">Top Dividend Payers</h2>
          <div className="card overflow-hidden">
            <div className="table-responsive">
              <table className="w-full text-sm">
                <thead className="bg-dse-blue text-white">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">#</th>
                    <th className="px-4 py-3 text-left font-medium">Company</th>
                    <th className="px-4 py-3 text-left font-medium hidden md:table-cell">Sector</th>
                    <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">DPS (TZS)</th>
                    <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">Total Payout</th>
                    <th className="px-4 py-3 text-right font-medium">Yield</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {topPayers.map((p: any, i: number) => (
                    <tr key={p.symbol}>
                      <td className="px-4 py-3 text-gray-400 font-medium">{i + 1}</td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-gray-900">{p.symbol}</div>
                        <div className="text-xs text-gray-500">{p.name}</div>
                      </td>
                      <td className="px-4 py-3 text-gray-500 hidden md:table-cell">{p.sector}</td>
                      <td className="px-4 py-3 text-right font-mono hidden sm:table-cell">
                        {Number(p.dividend_per_share).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right font-mono hidden sm:table-cell">
                        TZS {Number(p.total_payout).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-700">
                          {p.dividend_yield}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Sector Analysis Tab */}
      {tab === "sectors" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sectors.map((s: any) => (
            <div
              key={s.sector}
              className="card p-5 border-l-4 border-dse-blue hover:shadow-md transition-shadow"
            >
              <h3 className="font-bold text-lg text-gray-900">{s.sector}</h3>
              <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
                <div>
                  <span className="text-gray-400 text-xs uppercase tracking-wider">Companies</span>
                  <div className="font-semibold mt-0.5">{s.company_count}</div>
                </div>
                <div>
                  <span className="text-gray-400 text-xs uppercase tracking-wider">Avg Yield</span>
                  <div className="font-semibold text-dse-green mt-0.5">
                    {s.average_yield}%
                  </div>
                </div>
                <div>
                  <span className="text-gray-400 text-xs uppercase tracking-wider">Market Cap</span>
                  <div className="font-mono text-xs mt-0.5">
                    TZS {Number(s.total_market_cap).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400 text-xs uppercase tracking-wider">Best</span>
                  <div className="font-semibold text-dse-blue mt-0.5">
                    {s.best_performer}{" "}
                    <span className="text-gray-400 font-normal">({s.best_yield}%)</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Dividend Aristocrats Tab */}
      {tab === "aristocrats" && (
        <div>
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
            <h3 className="font-semibold text-amber-800">
              What are Dividend Aristocrats?
            </h3>
            <p className="text-sm text-amber-700 mt-1">
              Companies with 2+ consecutive years of dividend increases. These
              stocks have the strongest track record of rewarding shareholders.
            </p>
          </div>

          {aristocrats.length === 0 ? (
            <div className="card p-8 text-center text-gray-400">
              No dividend aristocrats found with available data.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {aristocrats.map((a: any, i: number) => (
                <div
                  key={a.symbol}
                  className="card p-5 relative hover:shadow-md transition-shadow"
                >
                  {i < 3 && (
                    <div className="absolute top-3 right-3 bg-amber-100 text-amber-800 text-xs font-bold px-2 py-1 rounded-lg">
                      #{i + 1}
                    </div>
                  )}
                  <div className="font-bold text-lg text-gray-900">{a.symbol}</div>
                  <div className="text-sm text-gray-500">{a.name}</div>
                  <div className="text-xs text-gray-400 mt-1">{a.sector}</div>
                  <div className="grid grid-cols-2 gap-2 mt-4 text-sm">
                    <div className="bg-green-50 rounded-lg p-2 text-center">
                      <div className="text-green-700 font-bold text-lg">
                        {a.consecutive_increases}
                      </div>
                      <div className="text-xs text-green-600">
                        Consecutive
                      </div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-2 text-center">
                      <div className="text-blue-700 font-bold text-lg">
                        {a.dividend_yield}%
                      </div>
                      <div className="text-xs text-blue-600">Yield</div>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-2 text-center">
                      <div className="text-purple-700 font-bold text-lg">
                        {a.cagr}%
                      </div>
                      <div className="text-xs text-purple-600">CAGR</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <div className="text-gray-700 font-bold text-lg">
                        {a.years_of_data}
                      </div>
                      <div className="text-xs text-gray-600">Years Data</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Market Movers Tab */}
      {tab === "movers" && movers && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h2 className="text-lg font-bold text-green-700 mb-3">
              Biggest Dividend Increases
            </h2>
            <div className="space-y-2">
              {movers.biggest_increases?.map((m: any) => (
                <div
                  key={m.symbol}
                  className="card p-4 flex items-center justify-between hover:shadow-md transition-shadow border-l-4 border-green-500"
                >
                  <div>
                    <div className="font-semibold text-gray-900">{m.symbol}</div>
                    <div className="text-xs text-gray-500">{m.name}</div>
                    <div className="text-xs text-gray-400 mt-1 font-mono">
                      TZS {m.previous_dividend} → TZS {m.latest_dividend}
                    </div>
                  </div>
                  <div className="text-green-600 font-bold text-lg">
                    +{m.change_pct}%
                  </div>
                </div>
              ))}
              {(!movers.biggest_increases ||
                movers.biggest_increases.length === 0) && (
                <div className="text-gray-400 text-sm">No data available.</div>
              )}
            </div>
          </div>

          <div>
            <h2 className="text-lg font-bold text-red-700 mb-3">
              Biggest Dividend Decreases
            </h2>
            <div className="space-y-2">
              {movers.biggest_decreases?.map((m: any) => (
                <div
                  key={m.symbol}
                  className="card p-4 flex items-center justify-between hover:shadow-md transition-shadow border-l-4 border-red-400"
                >
                  <div>
                    <div className="font-semibold text-gray-900">{m.symbol}</div>
                    <div className="text-xs text-gray-500">{m.name}</div>
                    <div className="text-xs text-gray-400 mt-1 font-mono">
                      TZS {m.previous_dividend} → TZS {m.latest_dividend}
                    </div>
                  </div>
                  <div className="text-red-600 font-bold text-lg">
                    {m.change_pct}%
                  </div>
                </div>
              ))}
              {(!movers.biggest_decreases ||
                movers.biggest_decreases.length === 0) && (
                <div className="text-gray-400 text-sm">No data available.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Risk Scores Tab */}
      {tab === "risk" && (
        <div>
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <h3 className="font-semibold text-blue-800">
              Dividend Risk Scoring
            </h3>
            <p className="text-sm text-blue-700 mt-1">
              Stocks scored on dividend consistency (40%), growth trend (30%),
              and yield (30%). Higher score = lower risk. Not financial advice.
            </p>
          </div>

          <div className="card overflow-hidden">
            <div className="table-responsive">
              <table className="w-full text-sm">
                <thead className="bg-dse-blue text-white">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">#</th>
                    <th className="px-4 py-3 text-left font-medium">Company</th>
                    <th className="px-4 py-3 text-center font-medium">Overall</th>
                    <th className="px-4 py-3 text-center font-medium hidden md:table-cell">Consistency</th>
                    <th className="px-4 py-3 text-center font-medium hidden md:table-cell">Growth</th>
                    <th className="px-4 py-3 text-center font-medium hidden lg:table-cell">Yield</th>
                    <th className="px-4 py-3 text-center font-medium">Risk Level</th>
                    <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">Yield %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {riskMetrics.map((r: any, i: number) => (
                    <tr key={r.symbol}>
                      <td className="px-4 py-3 text-gray-400 font-medium">{i + 1}</td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-gray-900">{r.symbol}</div>
                        <div className="text-xs text-gray-500">{r.name}</div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <ScoreBar value={r.overall_score} />
                      </td>
                      <td className="px-4 py-3 text-center hidden md:table-cell">
                        <ScoreBar value={r.consistency_score} />
                      </td>
                      <td className="px-4 py-3 text-center hidden md:table-cell">
                        <ScoreBar value={r.growth_score} />
                      </td>
                      <td className="px-4 py-3 text-center hidden lg:table-cell">
                        <ScoreBar value={r.yield_score} />
                      </td>
                      <td className="px-4 py-3 text-center">
                        <RiskBadge level={r.risk_level} />
                      </td>
                      <td className="px-4 py-3 text-right font-mono hidden sm:table-cell">
                        {r.dividend_yield}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color: "blue" | "green" | "purple" | "gold";
}) {
  const colorClasses = {
    blue: "border-blue-200 text-blue-800 bg-blue-50",
    green: "border-green-200 text-green-800 bg-green-50",
    purple: "border-purple-200 text-purple-800 bg-purple-50",
    gold: "border-amber-200 text-amber-800 bg-amber-50",
  };
  return (
    <div className={`card border rounded-xl p-4 text-center ${colorClasses[color]}`}>
      <div className="text-xl sm:text-2xl font-bold">{value}</div>
      <div className="text-xs mt-1 opacity-75 font-medium">{label}</div>
    </div>
  );
}

function ScoreBar({ value }: { value: number }) {
  const color =
    value >= 70 ? "bg-green-500" : value >= 40 ? "bg-yellow-500" : "bg-red-400";
  return (
    <div className="flex items-center gap-2 justify-center">
      <div className="w-16 bg-gray-200 rounded-full h-2">
        <div
          className={`${color} h-2 rounded-full transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs font-mono text-gray-600">{value}</span>
    </div>
  );
}

function RiskBadge({ level }: { level: string }) {
  const classes =
    level === "Low"
      ? "bg-green-100 text-green-800"
      : level === "Medium"
        ? "bg-yellow-100 text-yellow-800"
        : "bg-red-100 text-red-800";
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${classes}`}>
      {level}
    </span>
  );
}
