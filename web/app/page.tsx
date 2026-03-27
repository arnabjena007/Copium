"use client";

import { motion } from "framer-motion";
import { FloatingNavbar } from "../components/floating-navbar";
import { FeatureGrid } from "../components/feature-grid";
import { TestimonialSection } from "../components/testimonial-section";
import { DashboardPreview } from "../components/dashboard-preview";
import { AnomalyChart } from "../components/anomaly-chart";
import { FaqAccordion } from "../components/faq-accordion";
import { IntegrationsCloud } from "../components/integrations-cloud";
import { Footer } from "../components/footer";
import { VanishInput } from "../components/vanish-input";
import { TypewriterEffect } from "../components/typewriter-effect";
import { Box, Zap, Activity, BookOpen, Bot } from "lucide-react";
import { Instrument_Serif } from "next/font/google";

const instrumentSerif = Instrument_Serif({ weight: "400", subsets: ["latin"] });

export default function Page() {
  const placeholders = [
    "arn:aws:ec2:us-east-1:123456789012:instance/i-0abc1234",
    "arn:aws:rds:us-west-2:123456789012:db:prod-db",
    "arn:aws:lambda:eu-central-1:123456789012:function:sync",
  ];

  return (
    <div className="min-h-screen w-full bg-white relative overflow-x-hidden font-sans">
      {/* Amber Glow Background */}
      <div
        className="fixed inset-0 z-0"
        style={{
          backgroundImage: "radial-gradient(125% 125% at 50% 10%, #ffffff 40%, #f59e0b 100%)",
          backgroundSize: "100% 100%",
        }}
      />
      
      <FloatingNavbar />

      <main className="relative z-10 w-full pt-32 pb-16 flex flex-col items-center">
        {/* HERO SECTION */}
        <section className="w-full max-w-5xl mx-auto px-4 text-center mt-12 mb-16">
          
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
          >
            <h1 className="text-4xl md:text-7xl font-extrabold tracking-tight mb-8 leading-tight text-brand-slate drop-shadow-sm">
              Find and fix <span className="text-brand-orange">cloud cost leaks</span> in seconds
            </h1>
          </motion.div>
          
          <motion.p
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
            className={`text-2xl md:text-3xl text-slate-500 mb-12 max-w-3xl mx-auto leading-relaxed ${instrumentSerif.className}`}
          >
            A focused audit experience that reveals what matters and removes what doesn’t.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4, ease: "easeOut" }}
            className="w-full max-w-3xl mx-auto mb-10 p-2"
          >
            <VanishInput 
              placeholders={placeholders} 
              onChange={() => {}} 
              onSubmit={(e) => { 
                e.preventDefault(); 
                window.location.href="https://copium-hizs9rmhxfvw8fqkt7rjk2.streamlit.app"; 
              }} 
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5, ease: "easeOut" }}
            className="flex flex-wrap justify-center gap-4 text-slate-600 font-medium"
          >
             <button className="flex items-center gap-2 hover:text-brand-slate transition-colors bg-white/70 backdrop-blur-md px-5 py-2.5 border border-slate-200 rounded-xl shadow-sm hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] hover:-translate-y-1 duration-300"><Box size={18}/> Bulk Scan</button>
             <button className="flex items-center gap-2 hover:text-brand-slate transition-colors bg-white/70 backdrop-blur-md px-5 py-2.5 border border-slate-200 rounded-xl shadow-sm hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] hover:-translate-y-1 duration-300"><Activity size={18}/> Compare</button>
             <button className="flex items-center gap-2 hover:text-brand-slate transition-colors bg-white/70 backdrop-blur-md px-5 py-2.5 border border-slate-200 rounded-xl shadow-sm hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] hover:-translate-y-1 duration-300"><BookOpen size={18}/> Schema</button>
             <button className="flex items-center gap-2 hover:text-brand-slate transition-colors bg-white/70 backdrop-blur-md px-5 py-2.5 border border-slate-200 rounded-xl shadow-sm hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] hover:-translate-y-1 duration-300"><Bot size={18}/> AI SuitePRO</button>
             <button className="flex items-center gap-2 text-brand-orange bg-orange-50 px-5 py-2.5 rounded-xl transition-transform hover:-translate-y-1 duration-300 font-bold">+12 more &rarr;</button>
          </motion.div>
        </section>

        {/* MODULAR SECTIONS */}
        <FeatureGrid />

        <section className="mb-32 w-full max-w-6xl mx-auto px-4 md:px-6">
          <div className="bg-[#0B0F17] rounded-3xl overflow-hidden shadow-[0_10px_40px_rgba(0,0,0,0.15)] relative flex flex-col md:flex-row items-center cursor-default">
            
            {/* Context Layer */}
            <div className="md:w-1/2 p-10 md:p-14 z-10 relative">
              <h2 className="text-3xl md:text-[2.8rem] font-extrabold text-white mb-5 leading-[1.15] tracking-tight">
                Engineered to catch <br className="hidden md:block"/> <span className="text-brand-orange">mass traffic bursts</span>
              </h2>
              <p className="text-slate-400 text-lg md:text-xl font-medium mb-8 leading-relaxed max-w-md">
                Keep your financial pipelines running smoothly while our engines intercept idle resources and viral-load spikes before they map to your billing cycle.
              </p>
              <button className="text-brand-orange font-bold flex items-center gap-2 hover:gap-3 transition-all text-lg tracking-wide hover:text-orange-400">
                Interceptor Docs &rarr;
              </button>
            </div>

            {/* Aesthetic Graph Background Layer */}
            <div className="md:w-1/2 h-[350px] md:h-[450px] w-full relative z-0 overflow-hidden opacity-90 md:opacity-100 flex items-center justify-end">
               
               {/* Fade gradient so the graph blends into the text horizontally */}
               <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-[#0B0F17] to-transparent z-10 pointer-events-none max-md:hidden" />
               <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#0B0F17] to-transparent z-10 pointer-events-none md:hidden" />

               <div className="absolute inset-0 w-[120%] -right-[15%] h-[120%] top-[-10%] flex items-center opacity-80 pointer-events-auto"> 
                 <AnomalyChart className="scale-105 translate-y-6 md:translate-y-8" />
               </div>
            </div>

          </div>
        </section>
        
        <DashboardPreview />
        
        <TestimonialSection />
        
        <FaqAccordion />

      </main>

      {/* Scroll-convergence CTA — sits outside main, full-bleed */}
      <IntegrationsCloud />
      
      <Footer />
    </div>
  );
}
