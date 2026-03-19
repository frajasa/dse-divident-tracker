"use client";

import { useState } from "react";
import { calculateTax } from "@/lib/api";

// Pre-filled DSE stocks with their last known dividends
const DSE_STOCKS = [
  { symbol: "TBL", name: "Tanzania Breweries", lastDiv: 818 },
  { symbol: "NMB", name: "NMB Bank", lastDiv: 730 },
  { symbol: "TCC", name: "Tanzania Cigarette Co", lastDiv: 550 },
  { symbol: "TPCC", name: "Tanzania Portland Cement", lastDiv: 230 },
  { symbol: "CRDB", name: "CRDB Bank", lastDiv: 75 },
  { symbol: "SWIS", name: "Swissport Tanzania", lastDiv: 140 },
  { symbol: "DSE", name: "DSE Plc", lastDiv: 120 },
  { symbol: "NICO", name: "NICO Insurance", lastDiv: 70 },
  { symbol: "TOL", name: "Tanzania Oxygen", lastDiv: 50 },
  { symbol: "VODA", name: "Vodacom Tanzania", lastDiv: 20.2 },
  { symbol: "AFRIPRISE", name: "Afriprise Holdings", lastDiv: 18 },
  { symbol: "DCB", name: "DCB Bank", lastDiv: 12 },
];

interface TaxResult {
  gross_dividend: string;
  tax_rate: string;
  tax_amount: string;
  net_dividend: string;
  effective_yield: string;
  dta_applied: boolean;
  dta_country: string | null;
}

export default function TaxPage() {
  const [shares, setShares] = useState(1000);
  const [dps, setDps] = useState(818);
  const [residency, setResidency] = useState("resident");
  const [investorType, setInvestorType] = useState("individual");
  const [country, setCountry] = useState("");
  const [purchasePrice, setPurchasePrice] = useState(0);
  const [result, setResult] = useState<TaxResult | null>(null);
  const [calculating, setCalculating] = useState(false);

  const handleCalculate = async () => {
    setCalculating(true);
    const data = await calculateTax({
      shares,
      dividend_per_share: dps,
      residency,
      investor_type: investorType,
      country: country || undefined,
      purchase_price: purchasePrice || undefined,
    });
    setResult(data);
    setCalculating(false);
  };

  const selectStock = (lastDiv: number) => {
    setDps(lastDiv);
  };

  return (
    <div>
      <h1 className="page-heading">Dividend Tax Calculator</h1>
      <p className="page-subtitle mb-6">
        Calculate your dividend withholding tax for DSE stocks. Tanzania charges
        10% for residents and 15% for non-residents.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
        {/* Calculator Form */}
        <div className="card p-5 sm:p-6">
          <h2 className="font-semibold text-lg mb-4 text-gray-900">Enter Details</h2>

          {/* Quick stock selector */}
          <div className="mb-5">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quick Select:
            </label>
            <div className="flex flex-wrap gap-2">
              {DSE_STOCKS.map((s) => (
                <button
                  key={s.symbol}
                  onClick={() => selectStock(s.lastDiv)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    dps === s.lastDiv
                      ? "bg-dse-blue text-white border-dse-blue shadow-sm"
                      : "bg-gray-50 hover:bg-gray-100 border-gray-200 text-gray-700"
                  }`}
                >
                  {s.symbol} ({s.lastDiv})
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Shares
              </label>
              <input
                type="number"
                value={shares}
                onChange={(e) => setShares(Number(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                min={1}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dividend Per Share (TZS)
              </label>
              <input
                type="number"
                value={dps}
                onChange={(e) => setDps(Number(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                min={0}
                step={0.01}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Residency Status
              </label>
              <select
                value={residency}
                onChange={(e) => setResidency(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="resident">
                  Resident (Mkazi wa Tanzania) — 10%
                </option>
                <option value="non_resident">
                  Non-Resident (Nje ya Tanzania) — 15%
                </option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Investor Type
              </label>
              <select
                value={investorType}
                onChange={(e) => setInvestorType(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="individual">Individual (Mtu binafsi)</option>
                <option value="company">Company (Kampuni)</option>
              </select>
            </div>

            {residency === "non_resident" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Country (for DTA check)
                </label>
                <select
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Select country...</option>
                  <option value="Canada">Canada</option>
                  <option value="Denmark">Denmark</option>
                  <option value="Finland">Finland</option>
                  <option value="India">India</option>
                  <option value="Italy">Italy</option>
                  <option value="Norway">Norway</option>
                  <option value="South Africa">South Africa</option>
                  <option value="Sweden">Sweden</option>
                  <option value="Zambia">Zambia</option>
                  <option value="Other">Other Country</option>
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Purchase Price Per Share (TZS) — optional
              </label>
              <input
                type="number"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(Number(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                min={0}
              />
              <p className="text-xs text-gray-400 mt-1">
                For yield calculation
              </p>
            </div>

            <button
              onClick={handleCalculate}
              disabled={calculating}
              className="w-full bg-dse-blue text-white py-3 rounded-lg font-semibold hover:bg-blue-800 transition disabled:opacity-50 shadow-sm"
            >
              {calculating ? "Inahesabu..." : "Hesabu Kodi (Calculate Tax)"}
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-6">
          {result && (
            <div className="card p-5 sm:p-6">
              <h2 className="font-semibold text-lg mb-4 text-gray-900">Tax Breakdown</h2>

              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Shares</span>
                  <span className="font-mono font-semibold">
                    {shares.toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Dividend/Share</span>
                  <span className="font-mono font-semibold">
                    TZS {dps.toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between py-2.5 bg-green-50 px-3 rounded-lg">
                  <span className="text-gray-700 font-medium">
                    Gross Dividend
                  </span>
                  <span className="font-mono font-bold text-lg">
                    TZS {Number(result.gross_dividend).toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between py-2.5 bg-red-50 px-3 rounded-lg">
                  <span className="text-gray-700 font-medium">
                    Withholding Tax (
                    {(parseFloat(result.tax_rate) * 100).toFixed(0)}%)
                  </span>
                  <span className="font-mono font-bold text-red-600">
                    - TZS {Number(result.tax_amount).toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between py-3 bg-dse-blue text-white px-4 rounded-xl">
                  <span className="font-medium">Net Dividend</span>
                  <span className="font-mono font-bold text-xl">
                    TZS {Number(result.net_dividend).toLocaleString()}
                  </span>
                </div>

                {parseFloat(result.effective_yield) > 0 && (
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-gray-500">
                      Effective Yield (after tax)
                    </span>
                    <span className="font-mono font-bold text-dse-green">
                      {result.effective_yield}%
                    </span>
                  </div>
                )}

                {result.dta_applied && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
                    Double Taxation Agreement with {result.dta_country} applied
                    — reduced rate used.
                  </div>
                )}

                {/* USD equivalent */}
                <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-500">
                  <div className="font-medium mb-1">Approximate USD equivalent:</div>
                  <div className="font-mono">
                    Net: ~$
                    {(Number(result.net_dividend) / 2670).toLocaleString(
                      undefined,
                      { maximumFractionDigits: 2 }
                    )}{" "}
                    <span className="text-gray-400">(at TZS 2,670/USD)</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tax Info Card */}
          <div className="card p-5 sm:p-6">
            <h3 className="font-semibold mb-3 text-gray-900">Tanzania Dividend Tax Rules</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 text-gray-500 font-medium">Category</th>
                  <th className="text-right py-2 text-gray-500 font-medium">Rate</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="py-2.5">Resident Individual</td>
                  <td className="py-2.5 text-right font-mono font-medium">10%</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-2.5">Resident Company</td>
                  <td className="py-2.5 text-right font-mono font-medium">10%</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-2.5">Non-Resident Individual</td>
                  <td className="py-2.5 text-right font-mono font-medium">15%</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-2.5">Non-Resident Company</td>
                  <td className="py-2.5 text-right font-mono font-medium">15%</td>
                </tr>
              </tbody>
            </table>
            <p className="text-xs text-gray-400 mt-3">
              Tax is withheld at source. DTAs may reduce non-resident rates.
              Source: Income Tax Act, 2004.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
