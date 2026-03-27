"use client";

import { motion } from "framer-motion";

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
        <div className="bg-slate-50 border border-slate-200 rounded-2xl overflow-hidden shadow-inner">
          {/* Mock Header Tabs */}
          <div className="border-b border-slate-200 bg-white px-6 py-4 flex gap-8">
            <div className="text-brand-orange font-bold border-b-2 border-brand-orange pb-4 -mb-4 px-2">Results</div>
            <div className="text-slate-500 font-medium pb-4 -mb-4 px-2 cursor-pointer hover:text-slate-700 hover:border-b-2 hover:border-slate-300 transition-all">Cost Center</div>
            <div className="text-slate-500 font-medium pb-4 -mb-4 px-2 cursor-pointer hover:text-slate-700 hover:border-b-2 hover:border-slate-300 transition-all">Resources</div>
          </div>
          
          {/* Mock Table UI */}
          <div className="p-6">
            <div className="w-full">
              <div className="grid grid-cols-4 gap-4 pb-3 border-b border-slate-200 text-sm font-bold text-slate-400 uppercase tracking-wider">
                <div>Resource / ARN</div>
                <div>Anomaly Value</div>
                <div>Projected Status</div>
                <div className="text-right">Action</div>
              </div>
              
              {[1, 2, 3].map((row) => (
                <div key={row} className="grid grid-cols-4 gap-4 py-5 border-b border-slate-100 items-center">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-orange-100 flex-shrink-0" />
                    <div>
                      <div className="font-bold text-brand-slate text-sm">i-0a1b2c3d4e5f{row}</div>
                      <div className="text-xs text-slate-400">us-east-1</div>
                    </div>
                  </div>
                  <div className="font-mono text-red-500 font-medium">+$2,430.00</div>
                  <div>
                    <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold">Optimized Ready</span>
                  </div>
                  <div className="text-right">
                    <button className="text-sm font-bold text-brand-orange bg-orange-50 px-4 py-2 rounded-xl hover:bg-orange-100 transition-colors">Remediate</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
