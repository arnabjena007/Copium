"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, MessageSquare, Clock, ExternalLink } from "lucide-react";
import { useSlackDeepLink } from "../hooks/use-slack-deep-link";

interface Action {
  timestamp: string;
  action: string;
  resource_id: string;
  mode: string;
  success: boolean;
  message: string;
  insight?: string;
  origin?: "slack" | "system";
}

interface AuditFeedProps {
  actions: Action[];
}

export function AuditFeed({ actions }: AuditFeedProps) {
  const { openInSlack } = useSlackDeepLink();

  const handleSlackRedirect = (resourceId: string) => {
    const TEAM_ID = "T0AQ7027QSC"; 
    const CHANNEL_ID = "C0AP6AEQN3D";
    openInSlack(TEAM_ID, CHANNEL_ID);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
      <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
        <div className="flex items-center gap-3">
          <h3 className="text-xl font-bold text-brand-slate tracking-tight">Audit Trail & Action Feed</h3>
          <span className="bg-teal-50 text-brand-teal text-[10px] font-bold px-2 py-1 rounded-md border border-brand-teal/10 uppercase tracking-widest">
            Explainable AI: Mistral 7B
          </span>
          <div className="flex items-center gap-1.5 bg-indigo-50 text-indigo-600 text-[10px] font-bold px-2 py-1 rounded-md border border-indigo-100 uppercase tracking-widest">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-indigo-500"></span>
            </span>
            Slack Sync: Live
          </div>
        </div>
        <div className="flex items-center gap-2 text-slate-400 text-sm font-medium">
          <Clock size={16} /> 30s Polling Active
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-400 text-[10px] font-bold uppercase tracking-widest border-b border-slate-100">
              <th className="px-8 py-4">Timestamp</th>
              <th className="px-8 py-4">Event</th>
              <th className="px-8 py-4">Resource ID</th>
              <th className="px-8 py-4">Status</th>
              <th className="px-8 py-4 text-right">Context</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {actions.map((action, idx) => (
              <motion.tr
                key={`${action.resource_id}-${idx}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="group hover:bg-slate-50 transition-colors"
              >
                <td className="px-8 py-5">
                  <div className="text-brand-slate font-medium text-sm">
                    {new Date(action.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </div>
                  <div className="text-slate-400 text-[9px] uppercase font-bold mt-1">
                    {new Date(action.timestamp).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-8 py-5">
                  <div className="flex flex-col gap-1.5">
                    <span className="w-fit bg-teal-50 text-brand-teal border border-brand-teal/10 px-3 py-1.5 rounded-lg text-xs font-bold tracking-wide">
                      {action.action}
                    </span>
                    {action.origin === "slack" && (
                      <div className="flex items-center gap-1 text-[9px] font-bold text-indigo-500 uppercase tracking-tighter">
                        <MessageSquare size={10} /> Via Slack Approval
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-8 py-5">
                  <code className="text-brand-teal text-sm font-mono bg-slate-50 px-2 py-1 rounded border border-slate-100 opacity-90 group-hover:opacity-100 transition-opacity">
                    {action.resource_id}
                  </code>
                </td>
                <td className="px-8 py-5">
                  <div className="flex items-center gap-2">
                    {action.success ? (
                      <CheckCircle2 size={18} className="text-emerald-500" />
                    ) : (
                      <XCircle size={18} className="text-rose-500" />
                    )}
                    <span className={`text-sm font-semibold ${action.success ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {action.success ? "Success" : "Failed / Pending"}
                    </span>
                  </div>
                  {action.insight ? (
                    <div className="mt-2 text-xs bg-slate-50 border border-slate-100 p-2.5 rounded-xl text-slate-600 leading-relaxed relative group">
                      <div className="flex items-center gap-1.5 text-brand-teal font-bold text-[10px] uppercase mb-1 tracking-wider">
                        <span className="animate-pulse">✨</span> AI Insight
                      </div>
                      {action.insight}
                    </div>
                  ) : (
                    <div className="text-[11px] text-slate-400 truncate max-w-[180px] mt-1 italic">
                      {action.message}
                    </div>
                  )}
                </td>
                <td className="px-8 py-5 text-right">
                  <button
                    onClick={() => handleSlackRedirect(action.resource_id)}
                    className="inline-flex items-center gap-2 bg-[#4A154B] hover:bg-[#611f69] text-white px-4 py-2 rounded-xl text-xs font-bold transition-all transform hover:-translate-y-0.5 active:translate-y-0 shadow-lg shadow-[#4A154B]/20"
                  >
                    <MessageSquare size={14} /> Open in Slack
                  </button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {actions.length === 0 && (
        <div className="py-20 text-center text-slate-500 font-medium">
          No recent actions detected. Scanning infrastructure...
        </div>
      )}
    </div>
  );
}
