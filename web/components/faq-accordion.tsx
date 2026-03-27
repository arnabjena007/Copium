"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqs = [
  { q: "What is a cost-efficient AWS architecture?", a: "A cost-efficient architecture optimally blends On-Demand, Spot, and Reserved Instances while utilizing auto-scaling logic and minimizing idle subnets across your infrastructure." },
  { q: "How do I detect unused resources?", a: "CloudCFO runs a deep heuristic scan across your environment state instantly flagging orphaned EBS volumes, detached IPs, and idle NAT gateways." },
  { q: "What is a good cost benchmark?", a: "Industry standard efficiency scores strive for <15% wasted cloud spend vs. total optimized baseline. Our engine defaults to assessing performance against this rigorous standard." },
  { q: "How long does optimization take?", a: "Minutes. You paste your ARN, we visualize the leaks, and you execute our direct remediation scripts to instantly prune bloated infrastructure without code deployments." }
];

export function FaqAccordion() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggle = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <section id="faq" className="py-24 relative z-10 w-full max-w-3xl mx-auto px-6">
      <div className="text-center mb-16">
        <h2 className="text-4xl font-extrabold text-brand-slate tracking-tight mb-4">Common Questions</h2>
      </div>

      <div className="space-y-4">
        {faqs.map((faq, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
            className="bg-white border border-gray-100 rounded-3xl overflow-hidden shadow-[0_4px_20px_rgb(0,0,0,0.03)] cursor-pointer hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] transition-shadow"
            onClick={() => toggle(idx)}
          >
            <div className="p-6 flex justify-between items-center bg-white">
              <h3 className="font-bold text-lg text-brand-slate">{faq.q}</h3>
              <motion.div
                animate={{ rotate: openIndex === idx ? 180 : 0 }}
                transition={{ duration: 0.3 }}
                className="text-brand-orange"
              >
                <ChevronDown size={24} />
              </motion.div>
            </div>
            
            <AnimatePresence>
              {openIndex === idx && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                >
                  <div className="px-6 pb-6 text-slate-500 leading-relaxed border-t border-slate-50 pt-4">
                    {faq.a}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
