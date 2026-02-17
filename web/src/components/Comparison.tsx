"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Section from "./Section";
import data from "@/data/precomputed";

const sameCrime = data.same_crime as Record<
  string,
  Record<string, { race_stats: Record<string, { mean: number; median: number; count: number }> }>
>;
const offenses = Object.keys(sameCrime);

const RACE_COLORS: Record<string, string> = {
  White: "#94a3b8",
  Black: "#f43f5e",
  Hispanic: "#f59e0b",
};

export default function Comparison() {
  const [offense, setOffense] = useState("Drug Trafficking");
  const stats = sameCrime[offense]?.["All levels"]?.race_stats;

  if (!stats) return null;

  const maxMean = Math.max(...Object.values(stats).map((s) => s.mean));

  return (
    <Section id="comparison" dark={false}>
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        The Disparity
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-4">
        Same Offense. Different Sentence.
      </h2>
      <p className="text-white/50 max-w-2xl mb-10">
        Average sentence length in months, by race, for defendants convicted of the same federal offense.
        All other factors held equal.
      </p>

      <select
        value={offense}
        onChange={(e) => setOffense(e.target.value)}
        className="mb-10 rounded-lg border border-white/10 bg-slate-800 px-4 py-3 text-white w-full max-w-xs"
      >
        {offenses.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>

      <div className="space-y-6">
        {(["White", "Black", "Hispanic"] as const).map((race) => {
          const s = stats[race];
          if (!s) return null;
          const pct = (s.mean / maxMean) * 100;
          return (
            <div key={race}>
              <div className="flex items-baseline justify-between mb-2">
                <span className="text-lg font-semibold" style={{ color: RACE_COLORS[race] }}>
                  {race}
                </span>
                <span className="text-white/60 text-sm">
                  {s.mean.toFixed(1)} months avg · {s.count.toLocaleString()} cases
                </span>
              </div>
              <div className="h-10 w-full rounded-lg bg-slate-800 overflow-hidden">
                <motion.div
                  className="h-full rounded-lg"
                  style={{ backgroundColor: RACE_COLORS[race] }}
                  initial={{ width: 0 }}
                  whileInView={{ width: `${pct}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  viewport={{ once: true }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Offense-specific effect from regression */}
      {data.by_offense
        .filter((o: { Offense: string }) => o.Offense === offense)
        .map((o: { Offense: string; Black_Effect: number; N: number; Significance_Stars: string }) => (
          <div key={o.Offense} className="mt-10 grid gap-4 md:grid-cols-2">
            <div className="rounded-xl bg-slate-800/50 p-6 border border-white/5">
              <p className="text-white/50 text-sm mb-1">Black penalty for {o.Offense}</p>
              <p className="text-3xl font-bold text-rose-500">
                {o.Black_Effect > 0 ? "+" : ""}
                {o.Black_Effect} months {o.Significance_Stars}
              </p>
              <p className="text-white/40 text-sm mt-1">
                Based on {o.N.toLocaleString()} cases
              </p>
            </div>
            {stats.Hispanic && stats.White && (
              <div className="rounded-xl bg-slate-800/50 p-6 border border-white/5">
                <p className="text-white/50 text-sm mb-1">Hispanic vs White for {o.Offense}</p>
                <p className="text-3xl font-bold text-amber-400">
                  {(stats.Hispanic.mean - stats.White.mean) > 0 ? "+" : ""}
                  {(stats.Hispanic.mean - stats.White.mean).toFixed(1)} months
                </p>
                <p className="text-white/40 text-sm mt-1">
                  Raw average difference · {stats.Hispanic.count.toLocaleString()} Hispanic cases
                </p>
              </div>
            )}
          </div>
        ))}
    </Section>
  );
}
