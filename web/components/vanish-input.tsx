"use client";
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

export const VanishInput = ({
  placeholders,
  onChange,
  onSubmit,
}: {
  placeholders: string[];
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}) => {
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentPlaceholder((prev) => (prev + 1) % placeholders.length);
    }, 3000);
    return () => clearInterval(intervalId);
  }, [placeholders.length]);

  return (
    <form
      className="relative w-full max-w-2xl mx-auto bg-white h-16 rounded-full overflow-hidden shadow-2xl transition duration-200 border border-slate-100"
      onSubmit={onSubmit}
    >
      <input
        onChange={onChange}
        type="text"
        placeholder="Enter the AWS code..."
        autoComplete="new-password"
        autoCorrect="off"
        spellCheck="false"
        name="random_search_field"
        className="w-full h-full bg-transparent text-slate-800 text-lg sm:text-lg px-8 py-4 focus:outline-none placeholder-slate-400 font-medium"
      />
      


      <button
        type="submit"
        className="absolute right-2 top-2 bottom-2 px-8 rounded-full bg-brand-teal text-white font-bold text-md transition-all hover:scale-105 shadow-[0_0_15px_rgba(13,148,136,0.4)] hover:shadow-[0_0_25px_rgba(13,148,136,0.6)] flex items-center group overflow-hidden"
      >
        <span className="relative z-10">Sync to Audit</span>
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
      </button>
    </form>
  );
};
