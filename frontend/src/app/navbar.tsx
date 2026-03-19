"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { getUser, clearAuth, type AuthUser } from "@/lib/auth";

const NAV_LINKS = [
  { href: "/", label: "Dividends" },
  { href: "/yields", label: "Yields" },
  { href: "/analytics", label: "Analytics" },
  { href: "/tax", label: "Tax Calculator" },
  { href: "/portfolio", label: "Portfolio" },
  { href: "/alerts", label: "Alerts" },
  { href: "/education", label: "Learn" },
  { href: "/assistant", label: "AI Assistant" },
];

export default function NavBar() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setUser(getUser());
  }, []);

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    window.location.href = "/";
  };

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <nav className="bg-dse-blue text-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <a href="/" className="text-lg sm:text-xl font-bold tracking-tight flex items-center gap-2">
            <span className="hidden sm:inline text-dse-gold">DSE</span>
            <span className="sm:hidden text-dse-gold">DSE</span>
            <span className="hidden sm:inline">Dividend Tracker</span>
          </a>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden text-white p-2 rounded-lg hover:bg-white/10 transition"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className={`px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  isActive(link.href)
                    ? "bg-white/15 text-dse-gold"
                    : "text-white/80 hover:text-white hover:bg-white/10"
                }`}
              >
                {link.label}
              </a>
            ))}
            <div className="ml-2 pl-3 border-l border-white/20 flex items-center">
              {user ? (
                <div className="flex items-center gap-3">
                  <span className="text-dse-gold text-xs font-medium">
                    {user.name || user.phone}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg text-xs font-medium transition"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <a
                  href="/login"
                  className="bg-dse-gold/20 hover:bg-dse-gold/30 text-dse-gold px-4 py-1.5 rounded-lg text-sm font-medium transition"
                >
                  Login
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile nav */}
      <div
        className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out ${
          mobileOpen ? "max-h-[500px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="border-t border-white/10 px-4 py-3 space-y-1 bg-dse-blue/95 backdrop-blur-sm">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`block py-2.5 px-3 rounded-lg text-sm font-medium transition ${
                isActive(link.href)
                  ? "bg-white/15 text-dse-gold"
                  : "text-white/80 hover:text-white hover:bg-white/10"
              }`}
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <div className="border-t border-white/10 pt-3 mt-2">
            {user ? (
              <div className="flex items-center justify-between px-3">
                <span className="text-dse-gold text-sm font-medium">
                  {user.name || user.phone}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-sm font-medium transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <a
                href="/login"
                className="block text-center py-2.5 px-3 bg-dse-gold/20 text-dse-gold rounded-lg text-sm font-medium hover:bg-dse-gold/30 transition"
              >
                Login
              </a>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
