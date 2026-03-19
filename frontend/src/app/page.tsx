"use client";

import { useEffect, useState } from "react";
import { fetchDividends, fetchUpcoming } from "@/lib/api";

interface Dividend {
  id: number;
  symbol: string;
  company_name: string;
  financial_year: string;
  dividend_per_share: string;
  announcement_date: string | null;
  books_closure_date: string | null;
  payment_date: string | null;
  dividend_type: string;
  status: string;
}

export default function Home() {
  const [dividends, setDividends] = useState<Dividend[]>([]);
  const [upcoming, setUpcoming] = useState<Dividend[]>([]);
  const [year, setYear] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchDividends(year || undefined),
      fetchUpcoming(90),
    ]).then(([divs, up]) => {
      setDividends(divs);
      setUpcoming(up);
      setLoading(false);
    });
  }, [year]);

  const statusBadge = (status: string) => {
    if (status === "paid")
      return (
        <span className="inline-flex items-center bg-green-100 text-green-800 px-2.5 py-0.5 rounded-full text-xs font-medium">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></span>
          Paid
        </span>
      );
    if (status === "books_closed")
      return (
        <span className="inline-flex items-center bg-yellow-100 text-yellow-800 px-2.5 py-0.5 rounded-full text-xs font-medium">
          <span className="w-1.5 h-1.5 bg-yellow-500 rounded-full mr-1.5"></span>
          Books Closed
        </span>
      );
    return (
      <span className="inline-flex items-center bg-blue-100 text-blue-800 px-2.5 py-0.5 rounded-full text-xs font-medium">
        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-1.5"></span>
        Announced
      </span>
    );
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="page-heading">DSE Dividend Calendar</h1>
        <p className="page-subtitle">
          All dividend announcements from the Dar es Salaam Stock Exchange in
          one place.
        </p>
      </div>

      {/* Upcoming Dividends Alert */}
      {upcoming.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 sm:p-5 mb-6">
          <h2 className="font-semibold text-amber-800 mb-1">
            Upcoming Book Closures
          </h2>
          <p className="text-sm text-amber-700 mb-4">
            Buy before the books closure date to receive the dividend.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {upcoming.map((d) => (
              <div
                key={d.id}
                className="bg-white rounded-lg border border-amber-200 p-3 sm:p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-bold text-lg">{d.symbol}</div>
                    <div className="text-sm text-gray-500">{d.company_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-dse-green font-semibold">
                      TZS {Number(d.dividend_per_share).toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-400">per share</div>
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-100">
                  Books close: <span className="font-medium text-amber-700">{d.books_closure_date}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Year filter */}
      <div className="flex items-center gap-3 mb-4">
        <label className="text-sm font-medium text-gray-700">Filter by year:</label>
        <select
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
          value={year}
          onChange={(e) => setYear(e.target.value)}
        >
          <option value="">All Years</option>
          <option value="2026">2026</option>
          <option value="2025">2025</option>
          <option value="2024">2024</option>
          <option value="2023">2023</option>
          <option value="2022">2022</option>
          <option value="2021">2021</option>
          <option value="2020">2020</option>
        </select>
      </div>

      {/* Dividends Table */}
      <div className="card overflow-hidden">
        <div className="table-responsive">
          <table className="w-full text-sm">
            <thead className="bg-dse-blue text-white">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Company</th>
                <th className="px-4 py-3 text-left font-medium hidden sm:table-cell">Year</th>
                <th className="px-4 py-3 text-right font-medium">Dividend/Share</th>
                <th className="px-4 py-3 text-left font-medium hidden md:table-cell">Announced</th>
                <th className="px-4 py-3 text-left font-medium hidden lg:table-cell">Books Close</th>
                <th className="px-4 py-3 text-left font-medium hidden md:table-cell">Payment</th>
                <th className="px-4 py-3 text-center font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-gray-400">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-6 h-6 border-2 border-dse-blue border-t-transparent rounded-full animate-spin"></div>
                      Loading dividend data...
                    </div>
                  </td>
                </tr>
              ) : dividends.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-gray-400">
                    No dividend announcements found.
                  </td>
                </tr>
              ) : (
                dividends.map((d) => (
                  <tr key={d.id} className="hover:bg-blue-50/50">
                    <td className="px-4 py-3">
                      <div className="font-semibold text-gray-900">{d.symbol}</div>
                      <div className="text-xs text-gray-500">
                        {d.company_name}
                      </div>
                      <div className="text-xs text-gray-400 sm:hidden mt-0.5">{d.financial_year}</div>
                    </td>
                    <td className="px-4 py-3 text-gray-600 hidden sm:table-cell">{d.financial_year}</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-dse-green">
                      TZS {Number(d.dividend_per_share).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-gray-600 hidden md:table-cell">{d.announcement_date || "—"}</td>
                    <td className="px-4 py-3 text-gray-600 hidden lg:table-cell">{d.books_closure_date || "—"}</td>
                    <td className="px-4 py-3 text-gray-600 hidden md:table-cell">{d.payment_date || "—"}</td>
                    <td className="px-4 py-3 text-center">
                      {statusBadge(d.status)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
