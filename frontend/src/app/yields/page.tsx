"use client";

import { useEffect, useState } from "react";
import { fetchYields } from "@/lib/api";

interface YieldData {
  symbol: string;
  name: string;
  sector: string;
  current_price: string;
  last_dividend: string;
  financial_year: string;
  dividend_yield: string;
}

export default function YieldsPage() {
  const [yields, setYields] = useState<YieldData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchYields().then((data) => {
      setYields(data);
      setLoading(false);
    });
  }, []);

  const yieldColor = (y: number) => {
    if (y >= 5) return "text-green-700 bg-green-100";
    if (y >= 2) return "text-yellow-700 bg-yellow-100";
    return "text-red-700 bg-red-100";
  };

  const yieldBar = (y: number) => {
    const width = Math.min(y * 10, 100);
    const color = y >= 5 ? "bg-green-500" : y >= 2 ? "bg-yellow-500" : "bg-red-400";
    return (
      <div className="w-24 bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all duration-500`} style={{ width: `${width}%` }} />
      </div>
    );
  };

  return (
    <div>
      <h1 className="page-heading">Dividend Yields</h1>
      <p className="page-subtitle mb-6">
        Current dividend yield for all DSE stocks, ranked from highest to
        lowest. Higher yield = more income per shilling invested.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="card p-4 text-center border-l-4 border-green-500">
          <div className="text-2xl font-bold text-green-700">
            {yields.filter((y) => parseFloat(y.dividend_yield) >= 5).length}
          </div>
          <div className="text-sm text-green-600 font-medium">High Yield (&gt;5%)</div>
        </div>
        <div className="card p-4 text-center border-l-4 border-yellow-500">
          <div className="text-2xl font-bold text-yellow-700">
            {yields.filter((y) => {
              const v = parseFloat(y.dividend_yield);
              return v >= 2 && v < 5;
            }).length}
          </div>
          <div className="text-sm text-yellow-600 font-medium">Medium Yield (2-5%)</div>
        </div>
        <div className="card p-4 text-center border-l-4 border-red-400">
          <div className="text-2xl font-bold text-red-700">
            {yields.filter((y) => parseFloat(y.dividend_yield) < 2).length}
          </div>
          <div className="text-sm text-red-600 font-medium">Low Yield (&lt;2%)</div>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="table-responsive">
          <table className="w-full text-sm">
            <thead className="bg-dse-blue text-white">
              <tr>
                <th className="px-4 py-3 text-left font-medium">#</th>
                <th className="px-4 py-3 text-left font-medium">Company</th>
                <th className="px-4 py-3 text-left font-medium hidden md:table-cell">Sector</th>
                <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">Price (TZS)</th>
                <th className="px-4 py-3 text-right font-medium hidden sm:table-cell">Dividend (TZS)</th>
                <th className="px-4 py-3 text-right font-medium">Yield</th>
                <th className="px-4 py-3 text-center font-medium hidden sm:table-cell">Visual</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-gray-400">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-6 h-6 border-2 border-dse-blue border-t-transparent rounded-full animate-spin"></div>
                      Loading yields...
                    </div>
                  </td>
                </tr>
              ) : (
                yields.map((y, i) => {
                  const yieldVal = parseFloat(y.dividend_yield);
                  return (
                    <tr key={y.symbol}>
                      <td className="px-4 py-3 text-gray-400 font-medium">{i + 1}</td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-gray-900">{y.symbol}</div>
                        <div className="text-xs text-gray-500">{y.name}</div>
                      </td>
                      <td className="px-4 py-3 text-gray-500 hidden md:table-cell">{y.sector}</td>
                      <td className="px-4 py-3 text-right font-mono text-gray-700 hidden sm:table-cell">
                        {Number(y.current_price).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-gray-700 hidden sm:table-cell">
                        {Number(y.last_dividend).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${yieldColor(yieldVal)}`}
                        >
                          {y.dividend_yield}%
                        </span>
                      </td>
                      <td className="px-4 py-3 hidden sm:table-cell">
                        <div className="flex justify-center">
                          {yieldBar(yieldVal)}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
