"use client";

import { useEffect, useState } from "react";
import { calculatePortfolioTax } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";

const DSE_STOCKS = [
  { symbol: "TBL", name: "Tanzania Breweries", lastDiv: 818, price: 9710 },
  { symbol: "NMB", name: "NMB Bank", lastDiv: 730, price: 14370 },
  { symbol: "TCC", name: "Tanzania Cigarette Co", lastDiv: 550, price: 8800 },
  { symbol: "TPCC", name: "Tanzania Portland Cement", lastDiv: 230, price: 6790 },
  { symbol: "CRDB", name: "CRDB Bank", lastDiv: 75, price: 2800 },
  { symbol: "SWIS", name: "Swissport Tanzania", lastDiv: 140, price: 4500 },
  { symbol: "DSE", name: "DSE Plc", lastDiv: 120, price: 6390 },
  { symbol: "NICO", name: "NICO Insurance", lastDiv: 70, price: 3750 },
  { symbol: "TOL", name: "Tanzania Oxygen", lastDiv: 50, price: 2500 },
  { symbol: "VODA", name: "Vodacom Tanzania", lastDiv: 20.2, price: 850 },
  { symbol: "AFRIPRISE", name: "Afriprise Holdings", lastDiv: 18, price: 380 },
  { symbol: "DCB", name: "DCB Bank", lastDiv: 12, price: 685 },
];

interface Holding {
  symbol: string;
  company_name: string;
  shares: number;
  dividend_per_share: number;
  purchase_price: number;
}

interface PortfolioResult {
  holdings: Array<{
    symbol: string;
    company_name: string;
    shares: number;
    dividend_per_share: string;
    gross_dividend: string;
    tax_rate: string;
    tax_amount: string;
    net_dividend: string;
    effective_yield: string;
  }>;
  summary: {
    total_gross_dividend: string;
    total_tax: string;
    total_net_dividend: string;
    total_invested: string;
    portfolio_yield: string;
    residency: string;
  };
}

export default function PortfolioPage() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [selectedStock, setSelectedStock] = useState(DSE_STOCKS[0].symbol);
  const [shares, setShares] = useState(1000);
  const [residency, setResidency] = useState("resident");
  const [result, setResult] = useState<PortfolioResult | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }
    setAuthenticated(true);
  }, []);

  const addHolding = () => {
    const stock = DSE_STOCKS.find((s) => s.symbol === selectedStock);
    if (!stock) return;

    if (holdings.find((h) => h.symbol === stock.symbol)) {
      alert(`${stock.symbol} is already in your portfolio`);
      return;
    }

    setHoldings([
      ...holdings,
      {
        symbol: stock.symbol,
        company_name: stock.name,
        shares,
        dividend_per_share: stock.lastDiv,
        purchase_price: stock.price,
      },
    ]);
  };

  const removeHolding = (symbol: string) => {
    setHoldings(holdings.filter((h) => h.symbol !== symbol));
    setResult(null);
  };

  const calculatePortfolio = async () => {
    if (holdings.length === 0) return;
    const data = await calculatePortfolioTax({
      holdings,
      residency,
      investor_type: "individual",
    });
    setResult(data);
  };

  const totalInvested = holdings.reduce(
    (sum, h) => sum + h.shares * h.purchase_price,
    0
  );

  if (authenticated === null) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <div className="w-8 h-8 border-2 border-dse-blue border-t-transparent rounded-full animate-spin mb-3"></div>
        Loading...
      </div>
    );
  }

  const user = getUser();

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-2 gap-1">
        <h1 className="page-heading">Portfolio Dividend Projector</h1>
        {user && (
          <span className="text-sm text-gray-400">
            {user.name || user.phone}
          </span>
        )}
      </div>
      <p className="page-subtitle mb-6">
        Add your DSE holdings to see projected annual dividend income and tax
        breakdown.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        {/* Add Holdings */}
        <div className="card p-5 sm:p-6">
          <h2 className="font-semibold text-lg mb-4 text-gray-900">Add Stock</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Stock</label>
              <select
                value={selectedStock}
                onChange={(e) => setSelectedStock(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                {DSE_STOCKS.map((s) => (
                  <option key={s.symbol} value={s.symbol}>
                    {s.symbol} — {s.name} (Div: TZS {s.lastDiv})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Shares</label>
              <input
                type="number"
                value={shares}
                onChange={(e) => setShares(Number(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                min={1}
              />
            </div>
            <button
              onClick={addHolding}
              className="w-full bg-dse-green text-white py-2.5 rounded-lg font-medium hover:bg-green-700 transition shadow-sm"
            >
              + Add to Portfolio
            </button>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-100">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tax Status
            </label>
            <select
              value={residency}
              onChange={(e) => setResidency(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              <option value="resident">Resident (10% tax)</option>
              <option value="non_resident">Non-Resident (15% tax)</option>
            </select>
          </div>
        </div>

        {/* Holdings List */}
        <div className="lg:col-span-2">
          {holdings.length === 0 ? (
            <div className="card p-8 sm:p-12 text-center">
              <div className="text-4xl text-gray-300 mb-3">&#128188;</div>
              <p className="text-lg font-medium text-gray-500 mb-1">Your portfolio is empty</p>
              <p className="text-sm text-gray-400">
                Add stocks from the panel to project your dividend income.
              </p>
            </div>
          ) : (
            <>
              <div className="card overflow-hidden mb-4">
                <div className="table-responsive">
                  <table className="w-full text-sm">
                    <thead className="bg-dse-blue text-white">
                      <tr>
                        <th className="px-4 py-3 text-left font-medium">Stock</th>
                        <th className="px-4 py-3 text-right font-medium">Shares</th>
                        <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">Invested</th>
                        <th className="px-4 py-3 text-right font-medium hidden md:table-cell">Div/Share</th>
                        <th className="px-4 py-3 text-right font-medium">Gross Div</th>
                        <th className="px-4 py-3 text-center font-medium">Remove</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {holdings.map((h) => (
                        <tr key={h.symbol}>
                          <td className="px-4 py-3 font-semibold text-gray-900">{h.symbol}</td>
                          <td className="px-4 py-3 text-right font-mono">
                            {h.shares.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right font-mono hidden sm:table-cell">
                            TZS{" "}
                            {(h.shares * h.purchase_price).toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right font-mono hidden md:table-cell">
                            TZS {h.dividend_per_share.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right font-mono text-dse-green font-semibold">
                            TZS{" "}
                            {(
                              h.shares * h.dividend_per_share
                            ).toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <button
                              onClick={() => removeHolding(h.symbol)}
                              className="text-red-400 hover:text-red-600 text-xs font-medium transition"
                            >
                              Remove
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-gray-50 font-semibold border-t-2 border-gray-200">
                      <tr>
                        <td className="px-4 py-3 text-gray-900">TOTAL</td>
                        <td className="px-4 py-3 text-right font-mono">
                          {holdings
                            .reduce((s, h) => s + h.shares, 0)
                            .toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right font-mono hidden sm:table-cell">
                          TZS {totalInvested.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 hidden md:table-cell"></td>
                        <td className="px-4 py-3 text-right font-mono text-dse-green">
                          TZS{" "}
                          {holdings
                            .reduce(
                              (s, h) => s + h.shares * h.dividend_per_share,
                              0
                            )
                            .toLocaleString()}
                        </td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              <button
                onClick={calculatePortfolio}
                className="w-full bg-dse-blue text-white py-3 rounded-xl font-semibold hover:bg-blue-800 transition shadow-sm"
              >
                Calculate Tax & Net Income
              </button>

              {/* Results */}
              {result && (
                <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="card p-5 border-l-4 border-green-500">
                    <div className="text-sm text-green-700 mb-1 font-medium">
                      Total Gross Dividend
                    </div>
                    <div className="text-2xl font-bold text-green-800 font-mono">
                      TZS{" "}
                      {Number(
                        result.summary.total_gross_dividend
                      ).toLocaleString()}
                    </div>
                  </div>
                  <div className="card p-5 border-l-4 border-red-400">
                    <div className="text-sm text-red-700 mb-1 font-medium">
                      Total Tax Withheld
                    </div>
                    <div className="text-2xl font-bold text-red-800 font-mono">
                      TZS{" "}
                      {Number(result.summary.total_tax).toLocaleString()}
                    </div>
                  </div>
                  <div className="card p-5 border-l-4 border-blue-500">
                    <div className="text-sm text-blue-700 mb-1 font-medium">
                      Net Dividend (You Receive)
                    </div>
                    <div className="text-2xl font-bold text-blue-800 font-mono">
                      TZS{" "}
                      {Number(
                        result.summary.total_net_dividend
                      ).toLocaleString()}
                    </div>
                  </div>
                  <div className="card p-5 border-l-4 border-purple-500">
                    <div className="text-sm text-purple-700 mb-1 font-medium">
                      Portfolio Yield (after tax)
                    </div>
                    <div className="text-2xl font-bold text-purple-800">
                      {result.summary.portfolio_yield}%
                    </div>
                  </div>
                  <div className="sm:col-span-2 bg-dse-blue text-white rounded-xl p-5 shadow-sm">
                    <div className="text-sm opacity-80 mb-1">
                      Monthly Income Equivalent
                    </div>
                    <div className="text-3xl font-bold font-mono">
                      TZS{" "}
                      {Math.round(
                        Number(result.summary.total_net_dividend) / 12
                      ).toLocaleString()}
                      <span className="text-lg font-normal opacity-70">/month</span>
                    </div>
                    <div className="text-sm opacity-60 mt-1 font-mono">
                      ~$
                      {(
                        Number(result.summary.total_net_dividend) /
                        12 /
                        2670
                      ).toFixed(2)}{" "}
                      USD/month
                    </div>
                  </div>

                  {/* Per-holding breakdown */}
                  <div className="sm:col-span-2 card p-5">
                    <h3 className="font-semibold mb-3 text-gray-900">
                      Per-Stock Tax Breakdown
                    </h3>
                    <div className="table-responsive">
                      <table className="w-full text-sm">
                        <thead className="border-b border-gray-200">
                          <tr>
                            <th className="text-left py-2 font-medium text-gray-500">Stock</th>
                            <th className="text-right py-2 font-medium text-gray-500">Gross</th>
                            <th className="text-right py-2 font-medium text-gray-500">Tax</th>
                            <th className="text-right py-2 font-medium text-gray-500">Net</th>
                            <th className="text-right py-2 font-medium text-gray-500">Yield</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {result.holdings.map((h) => (
                            <tr key={h.symbol}>
                              <td className="py-2.5 font-semibold text-gray-900">{h.symbol}</td>
                              <td className="py-2.5 text-right font-mono">
                                TZS{" "}
                                {Number(h.gross_dividend).toLocaleString()}
                              </td>
                              <td className="py-2.5 text-right font-mono text-red-600">
                                -{Number(h.tax_amount).toLocaleString()}
                              </td>
                              <td className="py-2.5 text-right font-mono text-dse-green font-semibold">
                                TZS{" "}
                                {Number(h.net_dividend).toLocaleString()}
                              </td>
                              <td className="py-2.5 text-right font-mono">
                                {h.effective_yield}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
