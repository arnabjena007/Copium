"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Box } from "lucide-react";

export function FloatingNavbar({ transparentWhite = false }: { transparentWhite?: boolean }) {
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
        <a href="/" className="flex items-center gap-2 cursor-pointer group">
          <div className="w-10 h-10 bg-brand-teal text-white rounded-xl flex items-center justify-center shadow-lg group-hover:-translate-y-1 transition-transform">
            <Box size={22} className="stroke-[2.5]" />
          </div>
          <span className={`text-xl font-bold tracking-tight transition-colors duration-300 ${scrolled ? "text-brand-slate" : (transparentWhite ? "text-white" : "text-brand-slate")}`}>CloudCFO</span>
        </a>
        <div className={`hidden md:flex items-center gap-8 font-medium transition-colors duration-300 ${scrolled ? "text-slate-600" : (transparentWhite ? "text-white/80" : "text-slate-600")}`}>
          <a href="http://localhost:8501" className={`font-bold transition-all hover:-translate-y-0.5 ${scrolled ? "text-brand-teal hover:text-brand-teal-light" : (transparentWhite ? "text-white" : "text-brand-teal hover:text-brand-teal-light")}`}>Dashboard</a>
          <a href="#features" className={`transition-colors ${scrolled ? "hover:text-brand-teal" : (transparentWhite ? "hover:text-white" : "hover:text-brand-teal")}`}>Features</a>
          <a href="#faq" className={`transition-colors ${scrolled ? "hover:text-brand-teal" : (transparentWhite ? "hover:text-white" : "hover:text-brand-teal")}`}>FAQ</a>
        </div>
        <div className="flex items-center" />
      </div>
    </motion.nav>
  );
}
