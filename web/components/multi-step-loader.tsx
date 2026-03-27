"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

const loadingStates = [
  "[Syncing] Booting Slack Alert Service...",
  "[Syncing] Mapping Pydantic Data Models (CostAnomaly, IdleResource)...",
  "[Syncing] Testing Webhook handshakes...",
  "[Syncing] Consulting Llama 3.2 on local hardware...",
];

export function MultiStepLoader({ onComplete }: { onComplete: () => void }) {
  const [currentState, setCurrentState] = useState(0);

  useEffect(() => {
    if (currentState >= loadingStates.length) {
      onComplete();
      return;
    }
    const timer = setTimeout(() => {
      setCurrentState((prev) => prev + 1);
    }, 1500);
    return () => clearTimeout(timer);
  }, [currentState, onComplete]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: "600px", width: "100%" }}>
      {loadingStates.map((state, index) => {
        const isActive = index === currentState;
        const isDone = index < currentState;
        
        return (
          <motion.div 
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ 
              opacity: isDone ? 0.5 : isActive ? 1 : 0.3, 
              y: 0,
              scale: isActive ? 1.05 : 1
            }}
            transition={{ duration: 0.4 }}
            style={{
              padding: "1rem 1.5rem",
              borderRadius: "12px",
              background: isActive ? "rgba(94, 234, 212, 0.1)" : "rgba(8, 15, 28, 0.5)",
              border: `1px solid ${isActive ? "rgba(94, 234, 212, 0.4)" : "rgba(148, 163, 184, 0.1)"}`,
              display: isActive || isDone ? "flex" : "none",
              alignItems: "center",
              gap: "1rem",
              color: isActive ? "#5eead4" : "#97a6ba",
              fontWeight: isActive ? 600 : 400
            }}
          >
            {isDone && (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, color: "#5eead4" }}>
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            )}
            {isActive && (
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                style={{ width: "20px", height: "20px", borderRadius: "50%", border: "2px solid rgba(94,234,212,0.2)", borderTopColor: "#5eead4", flexShrink: 0 }}
              />
            )}
            <span style={{ fontSize: "1.1rem" }}>{state}</span>
          </motion.div>
        );
      })}
    </div>
  );
}
