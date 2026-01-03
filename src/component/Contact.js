import React from "react";

export default function Contact() {
  return (
    <section
      id="contact"
      className="min-h-screen py-20 px-6 flex flex-col items-center justify-center bg-gray-200"
      style={{ fontFamily: "Times New Roman, serif" }}
    >
      <h2 className="text-4xl md:text-5xl font-bold mb-12 text-center text-black">
        Get in Touch
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-16 w-full max-w-6xl">
        {/* Contact Info */}
        <div className="flex flex-col justify-center space-y-6">
          <h3 className="text-2xl font-semibold text-black">Contact Details</h3>
          <p className="text-lg text-black">📞 Phone: +977-XXXXXXXXX</p>
          <p className="text-lg text-black">📧 Email: username@example.com</p>
          <p className="text-lg text-black">📍 Location: Kathmandu, Nepal</p>

          <div className="flex space-x-4 mt-4">
            {/* <a
              href="#"
              className="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 transition"
            >
              Twitter
            </a> */}
            <a
              href="#"
              className="px-4 py-2 bg-blue-700 text-white rounded-lg shadow hover:bg-blue-800 transition"
            >
              LinkedIn
            </a>
            <a
              href="https://github.com/yoongles7/LSTM-Based-Trading-Trainer-Web-App"
              className="px-4 py-2 bg-gray-900 text-white rounded-lg shadow hover:bg-gray-800 transition"
            >
              GitHub
            </a>
          </div>
        </div>

        {/* Contact Form */}
        <div className="bg-white p-8 rounded-xl shadow-lg text-black">
          <h3 className="text-2xl font-semibold mb-6 text-black">Send Us a Message</h3>
          <form className="flex flex-col space-y-4">
            <input
              type="text"
              placeholder="Your Name"
              className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            />
            <input
              type="email"
              placeholder="Your Email"
              className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            />
            <textarea
              placeholder="Your Message"
              rows="5"
              className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg shadow hover:bg-blue-600 transition"
            >
              Send Message
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
