"use client";

import { motion } from "framer-motion";

const testimonials = [
  {
    name: "Sarah Jenkins",
    role: "VP of Engineering, Acme Corp",
    quote: "CloudCFO found $18,400 of idle EC2 waste our DevOps team missed completely.",
  },
  {
    name: "Michael Chen",
    role: "CTO, FinTech Scale",
    quote: "The A/B simulation engine is brilliant. Validated our shift to Graviton processors before committing.",
  },
  {
    name: "David Ross",
    role: "Head of Infrastructure",
    quote: "Finally, a tool that actually gives actionable remediation scripts instead of generic pie charts.",
  },
];

export function TestimonialSection() {
  return (
    <section id="testimonials" className="py-24 relative z-10 w-full max-w-7xl mx-auto px-6">
      <div className="text-center mb-16">
        <h2 className="text-4xl font-extrabold text-brand-slate tracking-tight mb-4">Trusted by modern CFOs</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {testimonials.map((t, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: "easeOut", delay: idx * 0.1 }}
            className="bg-white border border-gray-100 rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg transition-shadow duration-300"
          >
            <div className="flex gap-1 mb-6 text-brand-orange text-lg">
              ★★★★★
            </div>
            <p className="text-slate-600 font-medium text-lg leading-relaxed mb-8">"{t.quote}"</p>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-slate-200" />
              <div>
                <div className="font-bold text-brand-slate">{t.name}</div>
                <div className="text-sm text-slate-500">{t.role}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
