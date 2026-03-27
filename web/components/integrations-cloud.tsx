"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export function IntegrationsCloud() {
  const sectionRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "center center"],
  });

  const cardScale   = useTransform(scrollYProgress, [0, 1], [0.93, 1]);
  const cardOpacity = useTransform(scrollYProgress, [0, 0.25], [0, 1]);

  return (
    <section ref={sectionRef} className="w-full px-4 md:px-8 pb-10">
      <motion.div
        className="relative w-full min-h-[580px] bg-[#080B12] rounded-3xl overflow-hidden flex items-center justify-center"
        style={{
          scale: cardScale,
          opacity: cardOpacity,
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px)
          `,
          backgroundSize: "52px 52px",
        }}
      >
        {/* Radial mask — keeps center clear */}
        <div
          className="absolute inset-0 pointer-events-none z-0"
          style={{
            background:
              "radial-gradient(ellipse 55% 50% at 50% 50%, #080B12 30%, transparent 72%)",
          }}
        />

        {/* Center CTA */}
        <motion.div
          className="relative z-10 text-center px-8 select-none"
          style={{ opacity: useTransform(scrollYProgress, [0.2, 0.7], [0, 1]) }}
        >
          <motion.h2
            className="text-4xl md:text-6xl font-extrabold text-white mb-4 leading-tight tracking-tight"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, ease: "easeOut" }}
          >
            Connect your entire{" "}
            <span className="text-brand-orange">AWS stack</span>
          </motion.h2>
          <motion.p
            className="text-slate-400 text-lg md:text-xl max-w-md mx-auto mb-8"
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, delay: 0.15, ease: "easeOut" }}
          >
            One ARN. Every service. Zero blind spots.
          </motion.p>
          <motion.button
            className="bg-brand-orange text-white font-bold px-8 py-3.5 rounded-full text-lg shadow-[0_4px_24px_rgba(255,129,1,0.35)] hover:shadow-[0_8px_32px_rgba(255,129,1,0.45)] hover:-translate-y-0.5 transition-all duration-200"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.3 }}
            onClick={() => (window.location.href = "http://localhost:8501")}
          >
            Sync to Audit →
          </motion.button>
        </motion.div>
      </motion.div>
    </section>
  );
}
