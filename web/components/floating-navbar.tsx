"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Box } from "lucide-react";

export function FloatingNavbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-100" : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-2 cursor-pointer group">
          <div className="w-10 h-10 bg-brand-teal text-white rounded-xl flex items-center justify-center shadow-lg group-hover:-translate-y-1 transition-transform">
            <Box size={22} className="stroke-[2.5]" />
          </div>
          <span className="text-xl font-bold tracking-tight text-brand-slate">CloudCFO</span>
        </div>
        <div className="hidden md:flex items-center gap-8 font-medium text-slate-600">
          <a href="/dashboard" className="text-brand-teal font-bold hover:text-brand-teal-light transition-colors">Dashboard</a>
          <a href="#features" className="hover:text-brand-teal transition-colors">Features</a>
          <a href="#testimonials" className="hover:text-brand-teal transition-colors">Testimonials</a>
          <a href="#faq" className="hover:text-brand-teal transition-colors">FAQ</a>
        </div>
        <div className="flex items-center">
          <button className="bg-brand-slate text-white px-6 py-2.5 rounded-full font-bold hover:bg-brand-teal transition-colors shadow-md hover:shadow-xl hover:-translate-y-0.5 duration-200">
            Get Demo
          </button>
        </div>
      </div>
    </motion.nav>
  );
}
