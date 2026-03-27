"use client";

import { motion } from "framer-motion";
import { Activity, Layers, Shuffle } from "lucide-react";

const features = [
  {
    icon: <Activity size={24} className="text-brand-orange" />,
    title: "Cost Validation Testing",
    desc: "Simulate structural changes using real prod traffic endpoints without generating downtime.",
  },
  {
    icon: <Layers size={24} className="text-brand-orange" />,
    title: "Split Resource Optimization",
    desc: "Automatically map underutilized containers and reroute workloads to lower cost architectures dynamically.",
  },
  {
    icon: <Shuffle size={24} className="text-brand-orange" />,
    title: "Multi-variable Optimization",
    desc: "Process complex Spot, RI, and On-Demand blend scenarios instantly through our proprietary engine.",
  },
];

export function FeatureGrid() {
  return (
    <section id="features" className="py-24 relative z-10 w-full max-w-7xl mx-auto px-6">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="text-center mb-16"
      >
        <h2 className="text-4xl font-extrabold text-brand-slate tracking-tight mb-4">Precision Cost Mapping</h2>
        <p className="text-xl text-slate-500 max-w-2xl mx-auto">Automatically identify and isolate deep structural inefficiencies across your entire AWS fleet.</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: "easeOut", delay: idx * 0.1 }}
            className="group block bg-white border border-gray-100 rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_12px_40px_rgb(0,0,0,0.08)] hover:-translate-y-1 transition-all duration-300"
          >
            <div className="w-14 h-14 bg-orange-50 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
              {feat.icon}
            </div>
            <h3 className="text-xl font-bold text-brand-slate mb-3">{feat.title}</h3>
            <p className="text-slate-500 leading-relaxed mb-6">{feat.desc}</p>
            <div className="text-brand-orange font-bold flex items-center gap-2 group-hover:gap-3 transition-all cursor-pointer">
              Learn more <span>&rarr;</span>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
