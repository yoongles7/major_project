import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar, PieChart, Pie, Cell, Legend,
} from "recharts";

// Dummy Nepali portfolio data
const initialPortfolio = [
  { symbol: "NABIL", name: "Nabil Bank Ltd.", shares: 100, avgPrice: 1200, currentPrice: 1250 },
  { symbol: "HBL", name: "Himalayan Bank Ltd.", shares: 50, avgPrice: 950, currentPrice: 970 },
  { symbol: "NICA", name: "NIC Asia Bank Ltd.", shares: 80, avgPrice: 1200, currentPrice: 1180 },
  { symbol: "API", name: "Api Power Company Ltd.", shares: 200, avgPrice: 290, currentPrice: 295 },
  { symbol: "KBL", name: "Kumari Bank Ltd.", shares: 150, avgPrice: 320, currentPrice: 310 },
  { symbol: "CHCL", name: "Chilime Hydropower Co. Ltd.", shares: 120, avgPrice: 900, currentPrice: 920 },
  { symbol: "NEA", name: "Nepal Electricity Authority", shares: 50, avgPrice: 1500, currentPrice: 1550 },
];

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A28FFF", "#FF6699", "#33CC99", "#FF9933"];

export default function Profile() {
  const [portfolio, setPortfolio] = useState(initialPortfolio);
  const [portfolioHistory, setPortfolioHistory] = useState([]);

  // Function to simulate small price changes
  const simulatePriceChange = (stock) => {
    const changePercent = (Math.random() - 0.5) * 0.02; // ±1%
    const newPrice = stock.currentPrice * (1 + changePercent);
    return { ...stock, currentPrice: parseFloat(newPrice.toFixed(2)) };
  };

  // Auto-update prices every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setPortfolio(prev =>
        prev.map(stock => simulatePriceChange(stock))
      );

      // Update portfolio value history
      setPortfolioHistory(prev => [
        ...prev,
        { date: new Date().toLocaleTimeString(), value: portfolio.reduce((sum, s) => sum + s.shares * s.currentPrice, 0) }
      ].slice(-20)); // keep last 20 entries
    }, 5000);

    return () => clearInterval(interval);
  }, [portfolio]);

  // Calculations
  const totalInvestment = portfolio.reduce((sum, stock) => sum + stock.shares * stock.avgPrice, 0);
  const currentValue = portfolio.reduce((sum, stock) => sum + stock.shares * stock.currentPrice, 0);
  const profitLoss = currentValue - totalInvestment;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800 font-serif">PORTFOLIO</h1>
        <p className="text-sm text-gray-500">
          Overview of your investments and performance
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Total Investment" value={`NPR ${totalInvestment.toFixed(2)}`} />
        <Card title="Current Value" value={`NPR ${currentValue.toFixed(2)}`} />
        <Card
          title="Profit / Loss"
          value={`NPR ${profitLoss.toFixed(2)}`}
          valueClass={profitLoss >= 0 ? "text-green-600" : "text-red-600"}
        />
      </div>

      {/* Holdings Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">Holdings</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 text-sm">
            <thead className="bg-gray-100 text-gray-700">
              <tr>
                <th className="px-4 py-2 text-left">Symbol</th>
                <th className="px-4 py-2 text-left">Company</th>
                <th className="px-4 py-2 text-right">Shares</th>
                <th className="px-4 py-2 text-right">Avg Price</th>
                <th className="px-4 py-2 text-right">Current Price</th>
                <th className="px-4 py-2 text-right">Value</th>
                <th className="px-4 py-2 text-right">P/L</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.map((stock, idx) => {
                const value = stock.shares * stock.currentPrice;
                const pl = value - stock.shares * stock.avgPrice;
                return (
                  <tr key={idx} className="border-b border-gray-200">
                    <td className="px-4 py-2">{stock.symbol}</td>
                    <td className="px-4 py-2">{stock.name}</td>
                    <td className="px-4 py-2 text-right">{stock.shares}</td>
                    <td className="px-4 py-2 text-right">NPR {stock.avgPrice}</td>
                    <td className="px-4 py-2 text-right">NPR {stock.currentPrice}</td>
                    <td className="px-4 py-2 text-right">NPR {value.toFixed(2)}</td>
                    <td className={`px-4 py-2 text-right ${pl >= 0 ? "text-green-600" : "text-red-600"}`}>
                      NPR {pl.toFixed(2)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Line chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Portfolio Value Over Time</h3>
          <LineChart width={350} height={250} data={portfolioHistory}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#0088FE" strokeWidth={2} />
          </LineChart>
        </div>

        {/* Bar chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Profit/Loss Per Stock</h3>
          <BarChart
            width={350}
            height={250}
            data={portfolio.map(stock => ({
              symbol: stock.symbol,
              pl: stock.shares * stock.currentPrice - stock.shares * stock.avgPrice
            }))}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="symbol" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="pl" fill="#00C49F" />
          </BarChart>
        </div>

        {/* Pie chart */}
        <div className="bg-white rounded-lg shadow p-6 md:col-span-2">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Portfolio Allocation</h3>
          <PieChart width={400} height={300}>
            <Pie
              data={portfolio.map(stock => ({ name: stock.symbol, value: stock.shares * stock.currentPrice }))}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {portfolio.map((_, idx) => (
                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Legend />
            <Tooltip />
          </PieChart>
        </div>
      </div>
    </div>
  );
}

// Card component
function Card({ title, value, valueClass = "text-gray-800" }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center">
      <span className="text-gray-500 text-sm">{title}</span>
      <span className={`text-xl font-semibold ${valueClass}`}>{value}</span>
    </div>
  );
}
