"use client";

import { motion } from "framer-motion";
import Section from "./Section";
import data from "@/data/precomputed.json";

const offenses = data.human_cost.by_offense
  .filter((o: { Black_Effect_Mo: number }) => o.Black_Effect_Mo > 0)
  .sort((a: { Black_Effect_Mo: number }, b: { Black_Effect_Mo: number }) => b.Black_Effect_Mo - a.Black_Effect_Mo)
  .slice(0, 10);

const maxEffect = offenses[0]?.Black_Effect_Mo || 1;

export default function OffenseRanking() {
  return (
    <Section id="offense-ranking" dark={false}>
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        By Offense
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-4">
        Where the Gap Hits Hardest
      </h2>
      <p className="text-white/50 max-w-2xl mb-10">
        Extra months of prison time imposed on Black defendants compared to White defendants,
        by offense type — after controlling for all legal factors.
      </p>

      <div className="space-y-4">
        {offenses.map((o: { Offense: string; Black_Effect_Mo: number; N_Black: number }, i: number) => {
          const pct = (o.Black_Effect_Mo / maxEffect) * 100;
          const intensity = 0.4 + (o.Black_Effect_Mo / maxEffect) * 0.6;
          return (
            <motion.div
              key={o.Offense}
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              viewport={{ once: true }}
            >
              <div className="flex items-baseline justify-between mb-1">
                <span className="text-white/80 font-medium">{o.Offense}</span>
                <span className="text-rose-400 font-bold">+{o.Black_Effect_Mo} months</span>
              </div>
              <div className="h-8 w-full rounded-lg bg-slate-800 overflow-hidden">
                <motion.div
                  className="h-full rounded-lg"
                  style={{ backgroundColor: `rgba(244, 63, 94, ${intensity})` }}
                  initial={{ width: 0 }}
                  whileInView={{ width: `${pct}%` }}
                  transition={{ duration: 0.8, ease: "easeOut", delay: i * 0.08 }}
                  viewport={{ once: true }}
                />
              </div>
              <p className="text-white/30 text-xs mt-1">
                {o.N_Black.toLocaleString()} Black defendants
              </p>
            </motion.div>
          );
        })}
      </div>
    </Section>
  );
}
