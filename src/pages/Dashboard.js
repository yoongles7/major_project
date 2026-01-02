export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <p className="text-gray-500 text-sm">Total Balance</p>
          <p className="text-xl font-semibold">Rs. XXXXX</p>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <p className="text-gray-500 text-sm">Invested</p>
          <p className="text-xl font-semibold">Rs. XXXXX</p>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <p className="text-gray-500 text-sm">Profit / Loss</p>
          <p className="text-xl font-semibold text-green-600">+ Rs. XXX</p>
        </div>
      </div>

      {/* Stocks Section */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-4">My Stocks</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {["NABIL", "NLIC", "NRIC", "HBL"].map((stock) => (
            <div key={stock} className="border rounded p-3">
              <p className="font-medium">{stock}</p>
              <p className="text-sm text-gray-500">Current Price</p>
              <p className="font-semibold">Rs. XXX</p>
            </div>
          ))}
        </div>
      </div>

      {/* Chart Placeholder */}
      <div className="bg-white p-6 rounded shadow text-center text-gray-400">
        Candlestick Chart (NEPSE data)
      </div>
    </div>
  );
}
