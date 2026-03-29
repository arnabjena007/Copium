"use client";

import { motion } from "framer-motion";
import { ArchitectureDiagram } from "./architecture-diagram";

export function DashboardPreview() {
  return (
    <section className="py-24 relative z-10 w-full max-w-6xl mx-auto px-6 overflow-hidden">
      <motion.div
        initial={{ opacity: 0, x: 100 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="bg-white border border-gray-100 rounded-[2.5rem] p-4 md:p-8 shadow-[0_20px_60px_rgb(0,0,0,0.08)]"
      >
        {/* Dashboard Content Area */}
        <div className="rounded-2xl overflow-hidden shadow-inner bg-[#0B121F] p-4 md:p-6 border border-slate-200/50">
           <ArchitectureDiagram className="border border-cyan-500/10 shadow-2xl shadow-cyan-500/10" />
           
           {/* Simple legend or status line below */}
           <div className="mt-4 flex justify-between items-center text-[10px] md:text-xs text-slate-500 font-mono">
              <div className="flex gap-4">
                <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_5px_#22d3ee]" /> Source: US-EAST-1</span>
                <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-brand-teal" /> Target: #finops-alerts</span>
              </div>
              <div className="opacity-60 italic">Scan complete: 0.2ms latency</div>
           </div>
        </div>
      </motion.div>
    </section>
  );
}
