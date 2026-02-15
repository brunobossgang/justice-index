"use client";

import { motion } from "framer-motion";
import Section from "./Section";
import data from "@/data/precomputed.json";

const coefficients = data.overall.coefficients;

export default function Evidence() {
  return (
    <Section id="evidence">
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        The Evidence
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-4">
        The Numbers Don&apos;t Lie
      </h2>
      <p className="text-white/50 max-w-2xl mb-10">
        OLS regression on {data.overall.n_obs.toLocaleString()} federal sentencing cases.
        The model explains {(data.overall.r_squared * 100).toFixed(1)}% of sentence
        variation (R² = {data.overall.r_squared.toFixed(4)}).
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/10">
              <th className="py-3 px-4 text-sm text-white/50 font-medium">Variable</th>
              <th className="py-3 px-4 text-sm text-white/50 font-medium text-right">
                Effect (months)
              </th>
              <th className="py-3 px-4 text-sm text-white/50 font-medium text-right">
                Significant
              </th>
            </tr>
          </thead>
          <tbody>
            {coefficients.map(
              (c: { variable: string; effect: number; pvalue: number; significant: boolean }, i: number) => (
                <motion.tr
                  key={c.variable}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  viewport={{ once: true }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors"
                >
                  <td className="py-4 px-4 font-medium">{c.variable}</td>
                  <td
                    className={`py-4 px-4 text-right font-mono font-bold ${
                      c.effect > 0 ? "text-rose-500" : "text-emerald-400"
                    }`}
                  >
                    {c.effect > 0 ? "+" : ""}
                    {c.effect.toFixed(2)}
                  </td>
                  <td className="py-4 px-4 text-right">
                    {c.significant ? (
                      <span className="text-emerald-400 font-bold">p &lt; 0.05 ✓</span>
                    ) : (
                      <span className="text-white/30">n.s.</span>
                    )}
                  </td>
                </motion.tr>
              )
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-10 grid md:grid-cols-3 gap-6">
        <div className="rounded-xl bg-slate-800/50 border border-white/5 p-6 text-center">
          <p className="text-4xl font-black text-white/90">
            {(data.overall.r_squared * 100).toFixed(1)}%
          </p>
          <p className="text-white/40 text-sm mt-2">Variance explained (R²)</p>
        </div>
        <div className="rounded-xl bg-slate-800/50 border border-white/5 p-6 text-center">
          <p className="text-4xl font-black text-white/90">
            {data.overall.n_obs.toLocaleString()}
          </p>
          <p className="text-white/40 text-sm mt-2">Cases in model</p>
        </div>
        <div className="rounded-xl bg-slate-800/50 border border-white/5 p-6 text-center">
          <p className="text-4xl font-black text-rose-500">+3.85</p>
          <p className="text-white/40 text-sm mt-2">Black penalty (months)</p>
        </div>
      </div>
    </Section>
  );
}
