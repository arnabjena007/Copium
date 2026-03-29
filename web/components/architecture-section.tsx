"use client";

import { motion } from "framer-motion";
import { Cloud, Zap, MessageSquare, ShieldCheck, Activity, Cpu } from "lucide-react";

export function ArchitectureSection() {
  const beamVariants = {
    initial: { strokeDashoffset: 1000 },
    animate: {
      strokeDashoffset: 0,
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: "linear",
      },
    },
  };

  const particleVariants = {
    animate: {
      offsetDistance: ["0%", "100%"],
      opacity: [1, 1, 0],
      transition: {
        duration: 2.5,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  return (
    <section className="relative w-full min-h-[700px] bg-cyan-950 overflow-hidden flex flex-col items-center justify-center py-20">
      {/* Isometric Dot Grid Background */}
      <div 
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, #22d3ee 1.5px, transparent 0)`,
          backgroundSize: "40px 40px",
          transform: "perspective(1000px) rotateX(60deg) translateY(-200px) scale(3)",
        }}
      />

      {/* Content Container */}
      <div className="relative z-20 w-full max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 items-center gap-12 text-center md:text-left">
        
        {/* AWS Source Node */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="flex flex-col items-center"
        >
          <div className="w-24 h-24 bg-cyan-900/50 backdrop-blur-xl border border-cyan-400/30 rounded-[2rem] flex items-center justify-center shadow-[0_0_50px_rgba(34,211,238,0.2)] mb-6 group hover:scale-105 transition-transform duration-300">
            <Cloud size={48} className="text-cyan-400 group-hover:animate-pulse" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">AWS Infrastructure</h3>
          <p className="text-cyan-100/60 text-sm max-w-[200px]">EC2, Lambda, RDS, and S3 Cost Vitals</p>
        </motion.div>

        {/* Central Brain Node */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="flex flex-col items-center relative"
        >
          {/* Animated Glow Rings */}
          <div className="absolute inset-0 flex items-center justify-center -z-10">
             <motion.div 
               animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
               transition={{ duration: 4, repeat: Infinity }}
               className="w-48 h-48 rounded-full bg-cyan-500/10 blur-3xl"
             />
          </div>

          <div className="w-32 h-32 bg-gradient-to-br from-cyan-400 to-teal-500 rounded-3xl flex items-center justify-center shadow-[0_0_80px_rgba(34,211,238,0.4)] mb-8 transform rotate-3 hover:rotate-0 transition-transform duration-500">
            <Cpu size={64} className="text-cyan-950" />
          </div>
          <h3 className="text-3xl font-extrabold text-white mb-3 tracking-tighter uppercase italic">CloudCFO Intelligence</h3>
          <p className="text-cyan-300 font-mono text-xs mb-4">ML-DRIVEN ANOMALY ENGINE</p>
          
          <div className="flex gap-2">
            <span className="flex items-center gap-1.5 bg-cyan-900/40 px-3 py-1 rounded-full border border-cyan-500/20 text-[10px] text-cyan-200 font-bold tracking-widest uppercase">
              <ShieldCheck size={12} /> Guardrails Active
            </span>
          </div>
        </motion.div>

        {/* Slack Sink Node */}
        <motion.div 
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="flex flex-col items-center"
        >
          <div className="w-24 h-24 bg-slate-900/50 backdrop-blur-xl border border-cyan-400/20 rounded-[2rem] flex items-center justify-center shadow-[0_0_40px_rgba(34,211,238,0.1)] mb-6 group hover:scale-105 transition-transform duration-300">
             <MessageSquare size={44} className="text-brand-teal group-hover:rotate-12 transition-transform" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">Slack Collab Hub</h3>
          <p className="text-cyan-100/60 text-sm max-w-[200px]">Instant Alerts & Remote Remediation</p>
        </motion.div>

      </div>

      {/* SVG Lightning Beams & Particles */}
      <div className="absolute inset-0 pointer-events-none hidden md:block">
        <svg className="w-full h-full" overflow="visible">
          {/* Beam 1: AWS -> Brain */}
          <motion.path
            d="M 25% 50% Q 37.5% 50% 50% 50%"
            fill="none"
            stroke="url(#beamGradient)"
            strokeWidth="3"
            strokeDasharray="20 1000"
            variants={beamVariants}
            initial="initial"
            animate="animate"
          />
          
          {/* Beam 2: Brain -> Slack */}
          <motion.path
            d="M 50% 50% Q 62.5% 50% 75% 50%"
            fill="none"
            stroke="url(#beamGradient)"
            strokeWidth="3"
            strokeDasharray="20 1000"
            variants={beamVariants}
            initial="initial"
            animate="animate"
          />

          <defs>
            <linearGradient id="beamGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#22d3ee" stopOpacity="0" />
              <stop offset="50%" stopColor="#22d3ee" stopOpacity="1" />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>

        {/* Data Particles using secondary animation layer */}
        <div className="absolute top-1/2 left-[25%] w-[25%] h-[2px] overflow-visible">
            <motion.div 
              animate={{ x: ["0%", "100%"] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              className="w-4 h-4 rounded-full bg-cyan-400 blur-sm shadow-[0_0_15px_#22d3ee]"
            />
        </div>
        <div className="absolute top-1/2 left-[50%] w-[25%] h-[2px] overflow-visible">
            <motion.div 
              animate={{ x: ["0%", "100%"] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear", delay: 0.75 }}
              className="w-4 h-4 rounded-full bg-cyan-400 blur-sm shadow-[0_0_15px_#22d3ee]"
            />
        </div>
      </div>

      {/* Floating Status Indicator */}
      <motion.div 
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        className="mt-16 flex items-center gap-3 bg-cyan-400/10 px-6 py-2.5 rounded-2xl border border-cyan-400/30 backdrop-blur-md"
      >
        <div className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
        </div>
        <span className="text-cyan-100 font-bold text-sm tracking-wide">REAL-TIME SYNC ACTIVE</span>
      </motion.div>

    </section>
  );
}
