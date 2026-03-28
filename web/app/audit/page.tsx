"use client";

import { useEffect, useState } from "react";
import { MultiStepLoader } from "../../components/multi-step-loader";

export default function AuditPage() {
  const [complete, setComplete] = useState(false);

  useEffect(() => {
    if (complete) {
      setTimeout(() => {
        window.location.href = "https://kpi5dashboard.streamlit.app/";
      }, 500);
    }
  }, [complete]);

  return (
    <main className="page-shell" style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
      <MultiStepLoader onComplete={() => setComplete(true)} />
    </main>
  );
}
