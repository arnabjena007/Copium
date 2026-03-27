"use client";

import { motion } from "framer-motion";

export const TypewriterEffect = ({ text, className }: { text: string; className?: string }) => {
  const words = text.split(" ");
  return (
    <div className={`inline-block ${className}`}>
      {words.map((word, idx) => {
        return (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              duration: 0.1,
              delay: idx * 0.2, // Typewriter speed
            }}
            key={idx}
            className="inline-block"
          >
            {word}&nbsp;
          </motion.span>
        );
      })}
    </div>
  );
};
