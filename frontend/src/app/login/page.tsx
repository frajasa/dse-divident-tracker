"use client";

import { useState } from "react";
import { loginUser, registerUser } from "@/lib/api";
import { saveAuth } from "@/lib/auth";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = isRegister
        ? await registerUser(phone, password, name)
        : await loginUser(phone, password);

      saveAuth(data.access_token, {
        user_id: data.user_id,
        phone: data.phone,
        name: data.name,
      });

      window.location.href = "/portfolio";
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8 sm:mt-16 px-4">
      <div className="text-center mb-8">
        <div className="w-14 h-14 bg-dse-blue/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl font-bold text-dse-blue">DSE</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">
          {isRegister ? "Create Account" : "Welcome Back"}
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          {isRegister ? "Sign up to track your portfolio" : "Sign in to your account"}
        </p>
      </div>

      <div className="card p-6 sm:p-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5"
                placeholder="Your name"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone Number
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5"
              placeholder="+255 7XX XXX XXX"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5"
              placeholder="At least 6 characters"
              required
              minLength={6}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-dse-blue text-white py-3 rounded-xl font-semibold hover:bg-blue-800 transition disabled:opacity-50 shadow-sm"
          >
            {loading ? "Please wait..." : isRegister ? "Create Account" : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
            }}
            className="text-dse-blue font-semibold hover:underline"
          >
            {isRegister ? "Sign In" : "Create Account"}
          </button>
        </div>
      </div>
    </div>
  );
}
