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
  // Removed unused placeholder animation logic


  return (
    <form
      className="relative w-full flex justify-center py-4"
      onSubmit={onSubmit}
    >
      <button
        type="submit"
        className="px-10 py-5 rounded-full bg-brand-teal text-white font-bold text-xl transition-all hover:scale-105 shadow-[0_0_15px_rgba(13,148,136,0.4)] hover:shadow-[0_0_25px_rgba(13,148,136,0.6)] flex items-center group overflow-hidden"
      >
        <span className="relative z-10 tracking-wide">Sync to Audit</span>
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
      </button>
    </form>
  );
};
