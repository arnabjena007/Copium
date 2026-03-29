"use client";

import { motion } from "framer-motion";
import { 
  Activity, 
  Database, 
  Zap, 
  Trash2, 
  Cpu, 
  MessageSquare, 
  ShieldCheck, 
  Boxes, 
  CloudLightning,
  Settings
} from "lucide-react";

const LambdaIcon = () => (
  <svg viewBox="0 0 100 100" className="w-full h-full p-2">
    <defs>
      <linearGradient id="lambdaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#f90" />
        <stop offset="100%" stopColor="#ff9900" />
      </linearGradient>
    </defs>
    <rect width="100" height="100" rx="12" fill="url(#lambdaGrad)" />
    <path d="M30 75 L45 75 L55 55 L45 35 L30 35 M45 75 L70 35 L55 35 L30 75" fill="none" stroke="white" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const RDSIcon = () => (
  <svg viewBox="0 0 100 100" className="w-full h-full p-2">
    <defs>
      <linearGradient id="rdsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#3b48cc" />
        <stop offset="100%" stopColor="#242eb0" />
      </linearGradient>
    </defs>
    <rect width="100" height="100" rx="12" fill="url(#rdsGrad)" />
    <circle cx="50" cy="50" r="16" fill="none" stroke="white" strokeWidth="4" />
    <rect x="42" y="42" width="16" height="16" fill="white" opacity="0.8" />
    <path d="M25 25 L35 35 M75 25 L65 35 M25 75 L35 65 M75 75 L65 65" stroke="white" strokeWidth="4" strokeLinecap="round" />
  </svg>
);

const EC2Icon = () => (
  <svg viewBox="0 0 100 100" className="w-full h-full p-2">
    <defs>
      <linearGradient id="ec2Grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#f60" />
        <stop offset="100%" stopColor="#e60" />
      </linearGradient>
    </defs>
    <rect width="100" height="100" rx="12" fill="url(#ec2Grad)" />
    <rect x="35" y="35" width="30" height="30" rx="4" fill="none" stroke="white" strokeWidth="4" />
    <rect x="45" y="25" width="2" height="10" fill="white" />
    <rect x="53" y="25" width="2" height="10" fill="white" />
    <rect x="45" y="65" width="2" height="10" fill="white" />
    <rect x="53" y="65" width="2" height="10" fill="white" />
    <rect x="25" y="45" width="10" height="2" fill="white" />
    <rect x="25" y="53" width="10" height="2" fill="white" />
    <rect x="65" y="45" width="10" height="2" fill="white" />
    <rect x="65" y="53" width="10" height="2" fill="white" />
  </svg>
);

const analysisTriggers = [
  { id: "cost", label: "Cost Monitor", icon: <Activity className="text-cyan-400" /> },
  { id: "rds", label: "RDS Idle-Time", icon: <RDSIcon /> },
  { id: "ec2", label: "EC2 t4g Resize", icon: <EC2Icon /> },
  { id: "orphaned", label: "Orphaned Scans", icon: <Trash2 className="text-cyan-400" /> },
];

const remediationScripts = [
  { id: "ec2-fix", label: "EC2 Fix Script", icon: <EC2Icon /> },
  { id: "rds-fix", label: "RDS Fix Script", icon: <RDSIcon /> },
  { id: "lambda-fix", label: "Lambda Fix Script", icon: <LambdaIcon /> },
  { id: "s3-fix", label: "S3 Fix Script", icon: <Settings className="text-teal-400" /> },
  { id: "slack-fix", label: "Slack Notify", icon: <MessageSquare className="text-teal-400" /> },
];

export function ArchitectureDiagram({ className = "" }: { className?: string }) {
  const beamVariants = {
    initial: { strokeDashoffset: 1000 },
    animate: {
      strokeDashoffset: 0,
      transition: {
        duration: 2.5,
        repeat: Infinity,
        ease: "linear" as const,
      },
    },
  };

  return (
    <div className={`relative w-full h-[500px] overflow-hidden rounded-2xl bg-[#080B14] flex items-center justify-center p-4 md:p-8 ${className}`}>
      {/* Isometric Dot Grid Background */}
      <div 
        className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, #22d3ee 1.5px, transparent 0)`,
          backgroundSize: "40px 40px",
          transform: "perspective(1000px) rotateX(60deg) translateY(-100px) scale(3)",
        }}
      />

      <div className="relative z-20 w-full max-w-5xl mx-auto flex items-center justify-between gap-2 md:gap-4">
        
        {/* ANALYSIS COLUMN (LEFT) */}
        <div className="flex flex-col gap-4">
           <div className="text-[10px] font-bold text-cyan-500 uppercase tracking-widest text-center mb-1">Analysis</div>
           {analysisTriggers.map((trigger, idx) => (
             <motion.div 
               key={trigger.id}
               initial={{ opacity: 0, x: -20 }}
               whileInView={{ opacity: 1, x: 0 }}
               viewport={{ once: true }}
               transition={{ delay: idx * 0.1 }}
               className="flex items-center gap-3 bg-cyan-950/30 border border-cyan-500/10 p-2 md:px-3 md:py-2 rounded-xl group hover:border-cyan-500/40 transition-all cursor-default w-[110px] md:w-[150px]"
             >
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-cyan-950/50 flex items-center justify-center shadow-inner group-hover:bg-cyan-900 transition-colors">
                  {trigger.icon}
                </div>
                <div className="flex flex-col">
                   <span className="text-[10px] md:text-[11px] font-bold text-white whitespace-nowrap">{trigger.label}</span>
                   <span className="text-[8px] text-cyan-300/50">Continuous Scan</span>
                </div>
             </motion.div>
           ))}
        </div>

        {/* CENTRAL CONTROLLER HUB */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="flex flex-col items-center relative mx-2 md:mx-8"
        >
          <div className="absolute inset-0 flex items-center justify-center -z-10">
             <motion.div 
               animate={{ scale: [1, 1.3, 1], opacity: [0.1, 0.3, 0.1] }}
               transition={{ duration: 4, repeat: Infinity }}
               className="w-40 h-40 md:w-56 md:h-56 rounded-full bg-cyan-500/10 blur-3xl"
             />
          </div>

          <div className="w-24 h-24 md:w-32 md:h-32 bg-gradient-to-br from-cyan-400 to-teal-500 rounded-[2rem] flex items-center justify-center shadow-[0_0_60px_rgba(34,211,238,0.3)] mb-4">
            <Cpu size={56} className="text-cyan-950" />
          </div>
          <h4 className="text-xs md:text-sm font-extrabold text-white text-center leading-tight tracking-tight uppercase italic max-w-[120px]">
            AIOps Optimization Controller
          </h4>
          
          <div className="mt-4 flex gap-1">
            <span className="flex items-center gap-1 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30 text-[9px] text-cyan-300 font-bold uppercase tracking-widest shadow-[0_0_15px_rgba(34,211,238,0.2)]">
              <ShieldCheck size={10} /> Intelligence hub
            </span>
          </div>
        </motion.div>

        {/* REMEDIATION COLUMN (RIGHT) */}
        <div className="flex flex-col gap-3">
           <div className="text-[10px] font-bold text-teal-400 uppercase tracking-widest text-center mb-1">Remediations</div>
           {remediationScripts.map((script, idx) => (
             <motion.div 
               key={script.id}
               initial={{ opacity: 0, x: 20 }}
               whileInView={{ opacity: 1, x: 0 }}
               viewport={{ once: true }}
               transition={{ delay: idx * 0.1 }}
               className="flex items-center gap-3 bg-teal-950/20 border border-teal-500/10 p-2 md:px-3 md:py-2 rounded-xl group hover:border-teal-500/40 transition-all cursor-default w-[120px] md:w-[160px]"
             >
                <div className="flex flex-col text-right">
                   <span className="text-[10px] md:text-[11px] font-bold text-white whitespace-nowrap">{script.label}</span>
                   <span className="text-[8px] text-teal-300/50">Auto-Remediate</span>
                </div>
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-teal-950/50 flex items-center justify-center shadow-inner group-hover:bg-teal-900 transition-colors">
                  {script.icon}
                </div>
             </motion.div>
           ))}
        </div>

      </div>

      {/* SVG Lightning Beams & Fan-out */}
      <div className="absolute inset-0 pointer-events-none hidden md:block">
        <svg className="w-full h-full" overflow="visible">
          {/* Analysis -> Controller (Left) */}
          {[130, 185, 240, 295].map((y, i) => (
             <g key={`L-group-${i}`}>
               {/* Dotted Background Path */}
               <path
                 d={`M 170 ${y} Q 320 ${y} 430 250`}
                 fill="none"
                 stroke="rgba(34, 211, 238, 0.15)"
                 strokeWidth="1"
                 strokeDasharray="2 4"
               />
               {/* Animated Beam */}
               <motion.path
                 d={`M 170 ${y} Q 320 ${y} 430 250`}
                 fill="none"
                 stroke="url(#pipelineGradientL)"
                 strokeWidth="2"
                 strokeDasharray="40 1000"
                 variants={beamVariants}
                 initial="initial"
                 animate="animate"
                 transition={{ delay: i * 0.4 }}
               />
             </g>
          ))}

          {/* Controller -> Remediation (Right) */}
          {[120, 175, 230, 285, 340].map((y, i) => (
             <g key={`R-group-${i}`}>
               {/* Dotted Background Path */}
               <path
                 d={`M 570 250 Q 680 ${y} 830 ${y}`}
                 fill="none"
                 stroke="rgba(45, 212, 191, 0.15)"
                 strokeWidth="1"
                 strokeDasharray="2 4"
               />
               {/* Animated Beam */}
               <motion.path
                 d={`M 570 250 Q 680 ${y} 830 ${y}`}
                 fill="none"
                 stroke="url(#pipelineGradientR)"
                 strokeWidth="2"
                 strokeDasharray="40 1000"
                 variants={beamVariants}
                 initial="initial"
                 animate="animate"
                 transition={{ delay: i * 0.4 + 1 }}
               />
             </g>
          ))}

          <defs>
            <linearGradient id="pipelineGradientL" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#22d3ee" stopOpacity="0" />
              <stop offset="50%" stopColor="#22d3ee" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="pipelineGradientR" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2dd4bf" stopOpacity="0" />
              <stop offset="50%" stopColor="#2dd4bf" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#2dd4bf" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>

        {/* Data Particle Pulses */}
        <div className="absolute inset-0">
            {/* These should ideally follow paths, but for simplicity we'll add localized glows */}
        </div>
      </div>

      {/* Status Overlay Footer */}
      <div className="absolute bottom-4 left-0 right-0 px-8 flex justify-between items-center opacity-40">
         <div className="text-[9px] font-mono text-cyan-300">Continuous Data Extraction Active</div>
         <div className="text-[9px] font-mono text-teal-300">Remediation Pipelines: 5 Connected</div>
      </div>

    </div>
  );
}
