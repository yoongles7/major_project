import React from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

/* ------------------ DATA ------------------ */

// 1 Year portfolio value (monthly)
const portfolioHistory = [
  { month: "Jan", value: 900000 },
  { month: "Feb", value: 925000 },
  { month: "Mar", value: 960000 },
  { month: "Apr", value: 945000 },
  { month: "May", value: 980000 },
  { month: "Jun", value: 1010000 },
  { month: "Jul", value: 1035000 },
  { month: "Aug", value: 1020000 },
  { month: "Sep", value: 1048000 },
  { month: "Oct", value: 1070000 },
  { month: "Nov", value: 1082000 },
  { month: "Dec", value: 1090000 },
];

// Profit/Loss per stock
const profitLossData = [
  { name: "NABIL", pl: 45000 },
  { name: "NICA", pl: -12000 },
  { name: "HDHPC", pl: 28000 },
  { name: "UPPER", pl: 32000 },
  { name: "NLIC", pl: 15000 },
  { name: "PRVU", pl: 8000 },
];

// Sector allocation
const allocationData = [
  { name: "Banking", value: 38 },
  { name: "Hydropower", value: 27 },
  { name: "Insurance", value: 18 },
  { name: "Finance", value: 10 },
  { name: "Others", value: 7 },
];

// Watchlist
const watchlist = [
  { symbol: "NABIL", price: 525, change: "+2.1%" },
  { symbol: "NICA", price: 840, change: "-1.4%" },
  { symbol: "UPPER", price: 245, change: "+4.2%" },
  { symbol: "HDHPC", price: 190, change: "+3.6%" },
  { symbol: "PRVU", price: 215, change: "+0.9%" },
  { symbol: "NLIC", price: 720, change: "-0.6%" },
];

// Holdings
const holdings = [
  { name: "NABIL", qty: 100, avg: 480, current: 525 },
  { name: "NICA", qty: 50, avg: 860, current: 840 },
  { name: "UPPER", qty: 120, avg: 210, current: 245 },
  { name: "HDHPC", qty: 200, avg: 175, current: 190 },
  { name: "PRVU", qty: 80, avg: 205, current: 215 },
  { name: "NLIC", qty: 40, avg: 690, current: 720 },
];

// Recent paper trades
const recentTrades = [
  { date: "2026-01-01", stock: "UPPER", type: "BUY", qty: 50, price: 238 },
  { date: "2025-12-28", stock: "NABIL", type: "SELL", qty: 30, price: 520 },
  { date: "2025-12-26", stock: "HDHPC", type: "BUY", qty: 100, price: 182 },
  { date: "2025-12-24", stock: "PRVU", type: "BUY", qty: 80, price: 208 },
];

// AI prediction metrics
const predictions = [
  { stock: "NABIL", signal: "BUY", rsi: 61, trend: "Uptrend", volatility: "Medium" },
  { stock: "UPPER", signal: "BUY", rsi: 68, trend: "Strong Uptrend", volatility: "High" },
  { stock: "NICA", signal: "SELL", rsi: 72, trend: "Downtrend", volatility: "Medium" },
  { stock: "HDHPC", signal: "HOLD", rsi: 54, trend: "Sideways", volatility: "Low" },
];

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#0ea5e9"];

/* ------------------ COMPONENT ------------------ */

export default function Dashboard() {
  return (
    <div className="p-6 bg-gray-200 min-h-screen">
      <h1 className="text-3xl font-bold font-serif mb-6">
        DASHBOARD
      </h1>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6 bg-gray-100">
        <Summary title="Capital" value="Rs. 1,000,000" />
        <Summary title="Current Value" value="Rs. 1,090,000" />
        <Summary title="Net P/L" value="+ Rs. 90,000" positive />
        <Summary title="Active Trades" value="9" />
        <Summary title="Win Rate" value="64%" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6 bg-gray-100">
        <Card title="Portfolio Growth (1Y)">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={portfolioHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line
                dataKey="value"
                stroke="#6366f1"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Sector Allocation">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={allocationData}
                dataKey="value"
                cx="50%"
                cy="50%"
                outerRadius={90}
                isAnimationActive={false}
              >
                {allocationData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Profit / Loss by Stock">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={profitLossData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="pl" fill="#22c55e" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 bg-gray-100">
        <Table title="Holdings" headers={["Stock", "Qty", "Avg", "LTP", "P/L"]}>
          {holdings.map((h) => {
            const pl = (h.current - h.avg) * h.qty;
            return (
              <tr key={h.name}>
                <td>{h.name}</td>
                <td className="text-center">{h.qty}</td>
                <td className="text-center">{h.avg}</td>
                <td className="text-center">{h.current}</td>
                <td
                  className={`text-center font-semibold ${
                    pl >= 0 ? "text-green-600" : "text-red-500"
                  }`}
                >
                  {pl >= 0 ? "+" : ""}{pl}
                </td>
              </tr>
            );
          })}
        </Table>

        <Table title="Recent Paper Trades" headers={["Date", "Stock", "Type", "Qty", "Price"]}>
          {recentTrades.map((t, i) => (
            <tr key={i}>
              <td>{t.date}</td>
              <td>{t.stock}</td>
              <td className={t.type === "BUY" ? "text-green-600" : "text-red-500"}>
                {t.type}
              </td>
              <td className="text-center">{t.qty}</td>
              <td className="text-center">{t.price}</td>
            </tr>
          ))}
        </Table>
      </div>

      {/* AI Prediction Table */}
      <div className="mt-6 bg-white rounded-xl p-4 shadow bg-gray-100">
        <h2 className="font-semibold mb-3">AI Prediction Indicators</h2>
        <table className="w-full text-sm">
          <thead className="border-b text-gray-500">
            <tr>
              <th>Stock</th>
              <th>Signal</th>
              <th>RSI</th>
              <th>Trend</th>
              <th>Volatility</th>
            </tr>
          </thead>
          <tbody>
            {predictions.map((p) => (
              <tr key={p.stock} className="border-b last:border-none">
                <td>{p.stock}</td>
                <td className="font-semibold">{p.signal}</td>
                <td>{p.rsi}</td>
                <td>{p.trend}</td>
                <td>{p.volatility}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ------------------ UI COMPONENTS ------------------ */

const Summary = ({ title, value, positive }) => (
  <div className="bg-white p-4 rounded-xl shadow">
    <p className="text-sm text-gray-500">{title}</p>
    <h2 className={`text-xl font-bold ${positive && "text-green-600"}`}>
      {value}
    </h2>
  </div>
);

const Card = ({ title, children }) => (
  <div className="bg-white p-4 rounded-xl shadow">
    <h2 className="font-semibold mb-3">{title}</h2>
    {children}
  </div>
);

const Table = ({ title, headers, children }) => (
  <div className="bg-white p-4 rounded-xl shadow">
    <h2 className="font-semibold mb-3">{title}</h2>
    <table className="w-full text-sm">
      <thead className="border-b text-gray-500">
        <tr>
          {headers.map((h) => (
            <th key={h} className="text-left">{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>{children}</tbody>
    </table>
  </div>
);
