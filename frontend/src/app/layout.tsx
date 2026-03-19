import type { Metadata } from "next";
import "./globals.css";
import NavBar from "./navbar";

export const metadata: Metadata = {
  title: "DSE Dividend Tracker",
  description:
    "Track dividends, calculate tax, and project income for Dar es Salaam Stock Exchange stocks",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen flex flex-col">
        <NavBar />
        <main className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 sm:py-8 flex-1">
          {children}
        </main>
        <footer className="bg-gray-900 text-gray-400 text-center text-sm py-8 mt-auto border-t border-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
              <span className="font-semibold text-gray-300">DSE Dividend Tracker</span>
              <span className="text-xs text-gray-500">
                Not financial advice. Data sourced from DSE public announcements.
              </span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
