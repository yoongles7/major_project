import React from "react";
import chartImg from "../assets/chart.jpg";
import { Link, useNavigate } from "react-router-dom";

export default function Hero() {
  const navigate = useNavigate();
  return (
    <section
      id="home"
      className="w-full min-h-screen pt-24 pb-16 px-6 flex items-center bg-gray-900"
      style={{ fontFamily: "Times New Roman, serif" }}
    >
      <div className="max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

        {/* LEFT CONTENT */}
        <div>
          <p className="text-base mb-3 text-white">
            Learn Stock Trading Risk-Free with Virtual Money
          </p>

          <h1 className="text-4xl md:text-5xl font-bold mb-6 text-white leading-tight">
            LSTM Based <br />
            Trading Trainer <br />
            Web App
          </h1>

          <p className="text-white text-lg mb-8 max-w-xl">
            Train, test, and understand stock trading strategies using
            AI-powered LSTM models without risking real money.
          </p>

          <button
        
          className="px-6 py-3 bg-gray-800 text-white hover:bg-black transition">
            <Link to="/auth"> 
            Start Trading Free
            </Link>
          </button>
        </div>

        {/* RIGHT IMAGE */}
        <div className="w-full h-[320px] sm:h-[380px] md:h-[450px] rounded-xl overflow-hidden shadow-2xl">
          <img
            src={chartImg}
            alt="Stock chart"
            className="w-full h-full object-cover"
          />
        </div>

      </div>
    </section>
  );
}
