"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import AnimatedCounter from "./AnimatedCounter";
import data from "@/data/precomputed";

const blackEffect = data.overall.coefficients.find(
  (c: { variable: string }) => c.variable === "Black (vs White)"
)!;

const hispanicEffect = data.overall.coefficients.find(
  (c: { variable: string }) => c.variable === "Hispanic (vs White)"
)!;

// 108,157 extra years / 365.25 / 24 = ~12.35 extra hours per hour
// Per second: 12.35 / 3600 = 0.003430
const EXTRA_HOURS_PER_SECOND = data.human_cost.total_extra_years / 365.25 / 24 / 3600;

function LiveTicker() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds((s) => s + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const extraHours = (seconds * EXTRA_HOURS_PER_SECOND).toFixed(2);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 3, duration: 1 }}
      className="mt-8 flex items-center justify-center gap-2 text-sm text-white/40"
    >
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500" />
      </span>
      <span>
        Since you opened this page, Black defendants have collectively served{" "}
        <span className="text-rose-400 font-semibold">{extraHours} extra hours</span> in prison.
      </span>
    </motion.div>
  );
}

export default function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center px-6 text-center bg-slate-950">
      {/* subtle gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />

      <motion.div
        className="relative z-10"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.2, ease: "easeOut" }}
      >
        <p className="mb-4 text-sm font-medium uppercase tracking-[0.3em] text-rose-400/80">
          23 Years of Federal Sentencing Data
        </p>

        <h1 className="text-5xl font-extrabold leading-tight md:text-7xl lg:text-8xl">
          Same Crime.
          <br />
          <span className="text-rose-500">Different Time.</span>
        </h1>

        <p className="mx-auto mt-8 max-w-2xl text-lg text-white/60 md:text-xl">
          After controlling for offense severity, criminal history, and other legal factors,
          Black defendants receive an average of
        </p>

        <div className="mt-6 text-6xl font-black text-rose-500 md:text-8xl">
          +<AnimatedCounter value={blackEffect.effect} decimals={1} duration={2500} />
          <span className="text-4xl md:text-5xl"> months</span>
        </div>

        <p className="mt-4 text-lg text-white/50">
          longer in federal prison than White defendants
        </p>

        <div className="mt-6 rounded-xl bg-slate-800/50 border border-white/5 px-6 py-4 inline-block">
          <p className="text-white/40 text-sm mb-1">Meanwhile, Hispanic defendants receive</p>
          <p className="text-3xl font-bold text-amber-400">
            <AnimatedCounter value={Math.abs(hispanicEffect.effect)} decimals={2} duration={2000} />
            <span className="text-xl"> fewer months</span>
          </p>
          <p className="text-white/40 text-sm mt-1">than White defendants — a smaller but statistically significant difference</p>
        </div>

        <div className="mt-12 flex flex-wrap justify-center gap-8 text-white/40 text-sm">
          <div>
            <span className="block text-2xl font-bold text-white/80">
              <AnimatedCounter value={data.summary.total_cases} />
            </span>
            cases analyzed
          </div>
          <div>
            <span className="block text-2xl font-bold text-white/80">
              {data.summary.year_min}–{data.summary.year_max}
            </span>
            fiscal years
          </div>
          <div>
            <span className="block text-2xl font-bold text-white/80">
              R² = <AnimatedCounter value={data.overall.r_squared} decimals={2} />
            </span>
            model fit
          </div>
        </div>

        <LiveTicker />

        <div className="mt-8">
          <a
            href={`https://twitter.com/intent/tweet?text=${encodeURIComponent("Black defendants get 3.85 months longer for the same crime. 1.3M federal sentences exposed. samecrimedifferenttime.org via @Justice_Index")}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-white/10 hover:bg-white/20 px-5 py-2.5 text-sm font-medium text-white transition"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            Share on X
          </a>
        </div>

        <motion.div
          className="mt-8"
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <a href="#callout" className="text-white/30 text-3xl">
            ↓
          </a>
        </motion.div>
      </motion.div>
    </section>
  );
}
