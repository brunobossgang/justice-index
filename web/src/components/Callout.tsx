"use client";

import { motion } from "framer-motion";
import Section from "./Section";

const stats = [
  {
    offense: "Robbery",
    extra: "+11.48",
    desc: "Black defendants get nearly a FULL EXTRA YEAR",
    unit: "months",
  },
  {
    offense: "Drug Trafficking",
    extra: "+6.78",
    desc: "The most common federal offense — and the gap persists",
    unit: "months",
  },
];

export default function Callout() {
  return (
    <Section id="callout">
      <div className="grid md:grid-cols-2 gap-6">
        {stats.map((s, i) => (
          <motion.div
            key={s.offense}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.15 }}
            viewport={{ once: true }}
            className="rounded-2xl bg-gradient-to-br from-rose-600/90 to-rose-800/90 p-8 border border-rose-500/20"
          >
            <p className="text-white/70 text-sm font-medium uppercase tracking-wider mb-3">
              {s.offense}
            </p>
            <p className="text-5xl md:text-6xl font-black text-white">
              {s.extra}
            </p>
            <p className="text-white/80 text-sm mt-1 mb-4">extra months</p>
            <p className="text-white/60 text-sm leading-relaxed">
              {s.desc}
            </p>
          </motion.div>
        ))}
      </div>
    </Section>
  );
}
