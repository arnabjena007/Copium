"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { KpiCards } from "../../components/kpi-cards";
import { AuditFeed } from "../../components/audit-feed";
import { FloatingNavbar } from "../../components/floating-navbar";
import { Footer } from "../../components/footer";
import { RefreshCw, LayoutDashboard, ShieldCheck, Database, History, XCircle } from "lucide-react";

interface DashboardData {
  total_remediations_attempted: number;
  total_remediations_successful: number;
  total_monthly_savings_usd: number;
  recent_actions: any[];
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      // Use absolute URL for local development (8000) and relative for production
      const apiUrl = process.env.NODE_ENV === 'production' 
        ? "/api/dashboard" 
        : "http://localhost:8000/api/dashboard";
        
      const response = await fetch(apiUrl);
      if (!response.ok) throw new Error("Failed to fetch dashboard metrics");
      const result = await response.json();
      setData(result);
      setLastRefreshed(new Date());
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // 30-second polling interval as requested
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center gap-6">
        <motion.div 
          animate={{ rotate: 360 }} 
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        >
          <RefreshCw size={48} className="text-brand-teal" />
        </motion.div>
        <span className="text-slate-400 font-bold tracking-widest uppercase animate-pulse">
          Initializing Engine...
        </span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-brand-slate selection:bg-brand-teal/10">
      {/* Background Decor */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-teal/5 blur-[120px] rounded-full" />
      </div>

      <FloatingNavbar />

      <main className="relative z-10 pt-32 pb-24 px-4 md:px-8 max-w-7xl mx-auto">
        <section className="mb-12">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-10">
            <div>
              <div className="flex items-center gap-2 text-brand-teal font-bold tracking-widest text-xs uppercase mb-3">
                <LayoutDashboard size={14} /> CloudCFO Active Management
              </div>
              <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-brand-slate">
                FinOps Command Center
              </h1>
              <p className="text-slate-500 mt-4 text-lg font-medium max-w-2xl leading-relaxed">
                Real-time visibility into AWS remediation loops. Every automated action is cross-checked against your Slack configuration for maximum transparency.
              </p>
            </div>
            
            <div className="flex flex-col items-end gap-3 p-4 bg-white border border-slate-200 rounded-2xl shadow-sm">
              <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-wider text-slate-400">
                <div className="flex items-center gap-2"><ShieldCheck size={14} className="text-emerald-500" /> Boto3: Live</div>
                <div className="flex items-center gap-2"><Database size={14} className="text-brand-teal" /> Region: N.Virginia</div>
              </div>
              <div className="text-[10px] text-slate-600 font-bold flex items-center gap-1.5">
                <History size={10} /> Last Refresh: {lastRefreshed.toLocaleTimeString()}
              </div>
            </div>
          </div>

          {error && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-xl mb-8 flex items-center gap-3 font-medium"
            >
              <XCircle size={18} /> Engine Offline: {error}. Retrying connection...
            </motion.div>
          )}

          <KpiCards 
            attempted={data?.total_remediations_attempted || 0}
            successful={data?.total_remediations_successful || 0}
            savings={data?.total_monthly_savings_usd || 0}
          />
        </section>

        <section>
          <div className="flex items-center gap-3 mb-6">
            <h2 className="text-2xl font-bold tracking-tight text-brand-slate">Recent Infrastructure Operations</h2>
            <div className="h-px flex-1 bg-slate-200" />
            <button 
              onClick={fetchData} 
              className="text-slate-400 hover:text-brand-teal transition-colors p-2 rounded-lg hover:bg-slate-100"
              title="Manual Refresh"
            >
              <RefreshCw size={20} />
            </button>
          </div>
          
          <AuditFeed actions={data?.recent_actions || []} />
        </section>
      </main>

      <Footer />
    </div>
  );
}
