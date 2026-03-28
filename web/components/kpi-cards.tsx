"use client";

import { motion } from "framer-motion";
import { Zap, Target, TrendingUp } from "lucide-react";

interface KpiCardsProps {
  attempted: number;
  successful: number;
  savings: number;
}

export function KpiCards({ attempted, successful, savings }: KpiCardsProps) {
  const successRate = attempted > 0 ? (successful / attempted) * 100 : 0;

  const cards = [
    {
      label: "Operations Executed",
      value: attempted.toString(),
      icon: <Zap className="text-brand-teal" size={24} />,
      description: "Total remediations triggered",
    },
    {
      label: "Success Rate",
      value: `${successRate.toFixed(1)}%`,
      icon: <Target className="text-brand-teal" size={24} />,
      description: `${successful} successful actions`,
    },
    {
      label: "Monthly Savings",
      value: new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(savings),
      icon: <TrendingUp className="text-brand-teal" size={24} />,
      description: "Current projected ROI",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      {cards.map((card, idx) => (
        <motion.div
          key={card.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm relative overflow-hidden group hover:shadow-md transition-all duration-300"
        >
          {/* Subtle Glow Effect */}
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-brand-teal/5 blur-3xl rounded-full group-hover:bg-brand-teal/10 transition-all duration-500" />
          
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-teal-50 border border-brand-teal/10 rounded-xl">
              {card.icon}
            </div>
            <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              {card.label}
            </span>
          </div>
          
          <div className="text-3xl font-bold text-brand-slate mb-1 tracking-tight">
            {card.value}
          </div>
          <div className="text-slate-500 text-sm font-medium">
            {card.description}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
