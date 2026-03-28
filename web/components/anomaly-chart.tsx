"use client";

import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts";

const data = [
  { time: "00:00", cost: 120, baseline: 110, isAnomaly: false },
  { time: "04:00", cost: 135, baseline: 112, isAnomaly: false },
  { time: "08:00", cost: 140, baseline: 115, isAnomaly: false },
  { time: "12:00", cost: 490, baseline: 120, isAnomaly: true, detail: "Idle RDS Instance Left Running" },
  { time: "16:00", cost: 155, baseline: 118, isAnomaly: false },
  { time: "20:00", cost: 145, baseline: 115, isAnomaly: false },
  { time: "23:59", cost: 130, baseline: 110, isAnomaly: false },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload;
    if (dataPoint.isAnomaly) {
      return (
        <div className="bg-[#1E293B] text-slate-300 p-3 pt-2 rounded border border-slate-700 min-w-[150px] shadow-2xl font-mono text-[0.65rem] tracking-wider">
          <p className="text-brand-teal font-bold mb-[0.4rem] uppercase flex items-center gap-[6px]">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-teal animate-pulse"/> Anomaly Detected
          </p>
          <p className="text-slate-400 mb-[0.2rem] uppercase flex justify-between">
            <span>Time</span> <span className="text-white">{label}</span>
          </p>
          <p className="text-slate-400 uppercase flex justify-between tracking-normal">
            <span>Spike</span> <span className="text-white font-bold text-xs">${dataPoint.cost}</span>
          </p>
        </div>
      );
    }
    return (
      <div className="bg-[#1E293B] text-slate-300 p-2 px-3 rounded border border-slate-800 font-mono text-[0.65rem] tracking-wider uppercase">
        <p className="text-slate-400 flex justify-between gap-4"><span>Cost</span> <span className="text-white font-bold">${dataPoint.cost}</span></p>
      </div>
    );
  }
  return null;
};

export function AnomalyChart({ className }: { className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 1.2, ease: "easeOut" }}
      className={`w-full h-full relative ${className || ""}`}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 40, right: 30, left: 30, bottom: 40 }}>
          {/* Subtle design grid matching dark theme */}
          <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={true} />
          
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ stroke: "#334155", strokeWidth: 1, strokeDasharray: "4 4" }}
          />
          
          {/* The sleek design line */}
          <Line
            type="monotone"
            dataKey="cost"
            stroke="#0D9488"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: "#FFFFFF", stroke: "#0D9488", strokeWidth: 3 }}
            animationDuration={2500}
            animationEasing="ease-out"
          />
          
          {/* A hidden reference dot so the anomaly apex pulsates / stands out */}
          <ReferenceDot
            x="12:00"
            y={490}
            r={10}
            fill="rgba(13,148,136,0.15)"
            stroke="#0D9488"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
