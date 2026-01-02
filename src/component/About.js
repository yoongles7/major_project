import React from "react";

export default function About() {
  return (
    <section
      id="about"
      className="w-full min-h-screen flex items-center bg-gray-300 px-6"
      style={{ fontFamily: "Times New Roman, serif" }}
    >
      <div className="max-w-6xl mx-auto text-center">

        {/* Small Label */}
        <p className="text-sm uppercase tracking-widest text-gray-700 mb-4">
          About Our Platform
        </p>

        {/* Main Heading */}
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-8 leading-tight">
          Learn Stock Trading the <br />
          Smart & Risk-Free Way
        </h2>

        {/* Description */}
        <p className="text-lg md:text-xl text-gray-700 max-w-4xl mx-auto leading-relaxed">
          <span className="font-semibold">Trading Trainer</span> is an AI-powered
          educational web application designed for beginners and students who
          want to understand stock trading without financial risk.
          <br /><br />
          Using advanced <span className="font-semibold">LSTM-based models</span>,
          our platform simulates real market behavior, allowing users to practice
          trades with virtual money, analyze outcomes, and receive intelligent
          feedback on their strategies.
          <br /><br />
          Whether you are new to trading or want to sharpen your decision-making
          skills, Trading Trainer helps you build confidence before entering the
          real market.
        </p>

        {/* Optional Highlight Box */}
        <div className="mt-12 grid md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-xl shadow">
            <h3 className="text-xl font-semibold mb-2 text-black">Risk-Free Practice</h3>
            <p className="text-gray-700">
              Trade using virtual capital in realistic market conditions.
            </p>
          </div>

          <div className="p-6 bg-white rounded-xl shadow">
            <h3 className="text-xl font-semibold mb-2 text-black">AI-Driven Insights</h3>
            <p className="text-gray-700">
              Get feedback powered by LSTM models on every decision.
            </p>
          </div>

          <div className="p-6 bg-white rounded-xl shadow">
            <h3 className="text-xl font-semibold mb-2 text-black">Beginner Friendly</h3>
            <p className="text-gray-700">
              Designed especially for students and first-time traders.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
}
