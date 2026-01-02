import React from 'react'
import Navbar from '../component/Navbar';
import Hero from '../component/Hero';
import About from '../component/About';
import Features from '../component/Features';
import Contact from '../component/Contact';
import Footer from '../component/Footer'; 


export default function Home() {
  return (
    <div className="min-h-screen
  bg-gradient-to-br
  from-[#0b1220]
  via-[#0e1628]
  to-[#020617]
  text-white">
          <Navbar />
            <Hero />
            <About />
            <Features />
            <Contact />
            
            <Footer />
      
    </div>
  )
}
