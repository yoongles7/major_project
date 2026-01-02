import React from "react";
import { UserIcon } from "@heroicons/react/24/solid"; // Make sure you have heroicons installed

const members = [
  "Anajli Yadav",
  "Kritana Dahal",
  "Pritika Sharma",
  "Sandhya Nepal",
];

export default function TeamFooter() {
  return (
    <section
      className="py-16 px-6 bg-gray-800"
      style={{ fontFamily: "Times New Roman, serif" }}
    >
      {/* Team Section */}
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-8">Meet Our Team</h2>
        <div className="flex flex-wrap justify-center gap-10">
          {members.map((name, index) => (
            <div key={index} className="flex flex-col items-center">
              {/* Circle with User Icon */}
              <div className="w-24 h-24 bg-gray-300 rounded-full mb-3 flex items-center justify-center">
                <UserIcon className="w-12 h-12 text-white" />
              </div>
              <p className="font-semibold">{name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Section */}
      <footer className="border-t pt-6 text-center text-sm space-y-2">
        <p>
          <a href="#" className="text-white hover:underline">
            Github Repository
          </a>
        </p>
        <p>
          <a href="#" className="text-white hover:underline">
            Documentation
          </a>
        </p>
        <p className="mt-4 text-white">
          © 2025 - LSTM Based Trading Trainer Web App. All Rights Reserved.
        </p>
      </footer>
    </section>
  );
}
