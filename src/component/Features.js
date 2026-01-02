import React from "react";

const features = [
  {
    title: "Real Market Simulation",
    desc: "Trade with actual stock prices and market conditions",
  },
  {
    title: "Risk-Free Learning Environment",
    desc: "Practice trading with virtual capital without financial risk",
  },
  {
    title: "AI Powered Feedbacks",
    desc: "Get personalized feedback based on your trading patterns",
  },
  {
    title: "Performance Analytics",
    desc: "Track progress with insights, risk scores, and improvements",
  },
  {
    title: "Portfolio Management",
    desc: "Organize and track your virtual investments effectively",
  },
  {
    title: "Strategy Testing",
    desc: "Test different trading strategies before real investments",
  },
  {
    title: "Market Insights",
    desc: "Get real-time market trends and news for better decisions",
  },
  {
    title: "Learning Resources",
    desc: "Access tutorials and guides to improve your trading skills",
  },
];

export default function Features() {
  return (
    <section
      id="features"
      className="py-20 px-6 min-h-screen flex flex-col items-center justify-center bg-gray-800"
      style={{ fontFamily: "Times New Roman, serif" }}
    >
      <h2 className="text-4xl md:text-5xl font-bold mb-12 text-center text-grey-100">
        Key Features
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 w-full max-w-7xl">
        {features.map((feature, index) => (
          <div
            key={index}
            className="p-6 bg-white rounded-xl shadow-lg flex flex-col items-start hover:scale-105 transition-transform duration-300 bg-gray-200"
          >
            <div className="w-12 h-12 bg-gray-500 rounded-full mb-4 flex items-center justify-center font-bold text-xl">
              {index + 1}
            </div>
            <h3 className="font-bold text-lg mb-2 text-black">{feature.title}</h3>
            <p className="text-gray-700 text-sm">{feature.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
