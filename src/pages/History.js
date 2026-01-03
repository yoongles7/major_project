import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar, PieChart, Pie, Cell, Legend,
} from "recharts";

// Dummy trade history
const dummyHistory = [
  { date: "2026-01-01 10:00", symbol: "NABIL", company: "Nabil Bank Ltd.", type: "Buy", shares: 50, price: 1200 },
  { date: "2026-01-01 11:00", symbol: "HBL", company: "Himalayan Bank Ltd.", type: "Sell", shares: 30, price: 950 },
  { date: "2026-01-02 09:30", symbol: "NICA", company: "NIC Asia Bank Ltd.", type: "Buy", shares: 40, price: 1180 },
  { date: "2026-01-02 14:00", symbol: "API", company: "Api Power Company Ltd.", type: "Buy", shares: 100, price: 290 },
  { date: "2026-01-03 10:30", symbol: "NABIL", company: "Nabil Bank Ltd.", type: "Sell", shares: 20, price: 1250 },
  { date: "2026-01-03 15:00", symbol: "CHCL", company: "Chilime Hydropower Co. Ltd.", type: "Buy", shares: 60, price: 920 },
  { date: "2026-01-05 10:15", symbol: "NEA", company: "Nepal Electricity Authority", type: "Sell", shares: 20, price: 1550 },
];

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A28FFF", "#FF6699", "#33CC99", "#FF9933"];

export default function History() {
  const [history, setHistory] = useState(dummyHistory);

  // Calculate total trade value and profit/loss (mock)
  const historyWithPL = history.map(trade => {
    const value = trade.shares * trade.price;
    const pl = trade.type === "Sell" ? (Math.random() * value * 0.05) : 0; // simulate small P/L for sells
    return { ...trade, value, pl };
  });

  // Line chart data: cumulative P/L
  let cumulativePL = 0;
  const plHistory = historyWithPL.map(trade => {
    cumulativePL += trade.pl;
    return { date: trade.date, value: cumulativePL };
  });

  // Bar chart: P/L per stock
  const barData = [];
  historyWithPL.forEach(trade => {
    const index = barData.findIndex(d => d.symbol === trade.symbol);
    if (index !== -1) {
      barData[index].pl += trade.pl;
    } else {
      barData.push({ symbol: trade.symbol, pl: trade.pl });
    }
  });

  // Pie chart: count of trades per company
  const pieData = [];
  history.forEach(trade => {
    const index = pieData.findIndex(d => d.name === trade.symbol);
    if (index !== -1) {
      pieData[index].value += 1;
    } else {
      pieData.push({ name: trade.symbol, value: 1 });
    }
  });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800 font-serif">TRADING HISTORY</h1>
      <p className="text-medium text-gray-500">Overview of all executed trades</p>

      {/* Trades Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">All Trades</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 text-sm">
            <thead className="bg-gray-100 text-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Date/Time</th>
                <th className="px-4 py-2 text-left">Symbol</th>
                <th className="px-4 py-2 text-left">Company</th>
                <th className="px-4 py-2 text-left">Type</th>
                <th className="px-4 py-2 text-right">Shares</th>
                <th className="px-4 py-2 text-right">Price</th>
                <th className="px-4 py-2 text-right">Value</th>
                <th className="px-4 py-2 text-right">P/L</th>
              </tr>
            </thead>
            <tbody>
              {historyWithPL.map((trade, idx) => (
                <tr key={idx} className="border-b border-gray-200">
                  <td className="px-4 py-2">{trade.date}</td>
                  <td className="px-4 py-2">{trade.symbol}</td>
                  <td className="px-4 py-2">{trade.company}</td>
                  <td className={`px-4 py-2 ${trade.type === "Buy" ? "text-blue-600" : "text-green-600"}`}>
                    {trade.type}
                  </td>
                  <td className="px-4 py-2 text-right">{trade.shares}</td>
                  <td className="px-4 py-2 text-right">NPR {trade.price}</td>
                  <td className="px-4 py-2 text-right">NPR {trade.value.toFixed(2)}</td>
                  <td className={`px-4 py-2 text-right ${trade.pl >= 0 ? "text-green-600" : "text-red-600"}`}>
                    NPR {trade.pl.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Line chart: cumulative P/L */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Cumulative Profit/Loss Over Time</h3>
          <LineChart width={350} height={250} data={plHistory}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#FF8042" strokeWidth={2} />
          </LineChart>
        </div>

        {/* Bar chart: P/L per stock */}
        {/* <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Profit/Loss Per Stock</h3>
          <BarChart width={350} height={250} data={barData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="symbol" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="pl" fill="#00C49F" />
          </BarChart>
        </div> */}
        {/* Pie chart: Trades per company */}
        {/* <div className="bg-white rounded-lg shadow p-6 md:col-span-2">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Trades Distribution by Company</h3>
          <PieChart width={400} height={300}>
            <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
              {pieData.map((_, idx) => (
                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Legend />
            <Tooltip />
          </PieChart>
        </div> */} 
      </div>
    </div>
  );
}
