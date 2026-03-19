"use client";

import { useState, useRef, useEffect } from "react";
import { askAssistant } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  data?: any;
  suggestions?: string[];
}

const WELCOME_SUGGESTIONS = [
  "What is the highest yielding stock?",
  "Tell me about TBL",
  "Compare TBL and NMB",
  "Which stocks are safest?",
  "How do I start investing?",
  "What is dividend yield?",
  "When are the upcoming dividends?",
  "What are the best dividend stocks?",
];

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMessage: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await askAssistant(text);
      const assistantMessage: Message = {
        role: "assistant",
        content: response.answer || response.detail || "I received your question but couldn't generate a response.",
        data: response.data,
        suggestions: response.suggestions,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const renderMarkdown = (text: string) => {
    if (!text) return "";
    return text
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br />");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      <div className="mb-4">
        <h1 className="page-heading">AI Stock Assistant</h1>
        <p className="page-subtitle">
          Ask me anything about DSE stocks, dividends, tax, or investing
          strategies.
        </p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto card p-4 mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8 sm:py-12">
            <div className="w-16 h-16 bg-dse-blue/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">&#128200;</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              DSE Stock Assistant
            </h2>
            <p className="text-gray-400 mb-6 max-w-md mx-auto text-sm">
              I can help you with stock information, dividend analysis, tax
              calculations, investment education, and more.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg mx-auto">
              {WELCOME_SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-left text-sm bg-gray-50 hover:bg-dse-blue hover:text-white rounded-xl px-4 py-3 border border-gray-200 hover:border-dse-blue transition-all hover:shadow-sm"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-dse-blue text-white rounded-br-md"
                  : "bg-gray-50 border border-gray-200 rounded-bl-md"
              }`}
            >
              <div
                className="text-sm leading-relaxed"
                dangerouslySetInnerHTML={{
                  __html: renderMarkdown(msg.content),
                }}
              />

              {/* Comparison data table */}
              {msg.data?.comparison && (
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-1.5 font-medium">Metric</th>
                        {msg.data.comparison.map((c: any) => (
                          <th key={c.symbol} className="text-right py-1.5 font-medium">
                            {c.symbol}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-100">
                        <td className="py-1.5">Price</td>
                        {msg.data.comparison.map((c: any) => (
                          <td
                            key={c.symbol}
                            className="text-right py-1.5 font-mono"
                          >
                            TZS {Number(c.price).toLocaleString()}
                          </td>
                        ))}
                      </tr>
                      <tr className="border-b border-gray-100">
                        <td className="py-1.5">Dividend</td>
                        {msg.data.comparison.map((c: any) => (
                          <td
                            key={c.symbol}
                            className="text-right py-1.5 font-mono"
                          >
                            TZS {c.latest_dividend}
                          </td>
                        ))}
                      </tr>
                      <tr className="border-b border-gray-100">
                        <td className="py-1.5">Yield</td>
                        {msg.data.comparison.map((c: any) => (
                          <td
                            key={c.symbol}
                            className="text-right py-1.5 font-mono"
                          >
                            {c.dividend_yield}%
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="py-1.5">Growth</td>
                        {msg.data.comparison.map((c: any) => (
                          <td
                            key={c.symbol}
                            className="text-right py-1.5 font-mono"
                          >
                            {c.dividend_growth_cagr}
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}

              {/* Suggestion chips */}
              {msg.suggestions && msg.suggestions.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {msg.suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => sendMessage(s)}
                      className="text-xs bg-white border border-gray-200 rounded-full px-3 py-1.5 hover:bg-dse-blue hover:text-white hover:border-dse-blue transition-all font-medium"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-50 border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 text-sm text-gray-400 flex items-center gap-2">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
              </div>
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about DSE stocks, dividends, tax, investing..."
          className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-dse-blue/40 focus:border-dse-blue transition-shadow"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-dse-blue text-white px-6 py-3 rounded-xl font-medium hover:bg-blue-800 transition disabled:opacity-50 shadow-sm"
        >
          Send
        </button>
      </form>
    </div>
  );
}
