"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import Section from "./Section";
import AnimatedCounter from "./AnimatedCounter";
import data from "@/data/precomputed";

const cost = data.human_cost;
const lifetimes = Math.round(cost.total_extra_years / 365);

export default function HumanCost() {
  const counterRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(counterRef, { once: true, margin: "-100px" });

  return (
    <Section id="human-cost" dark={false}>
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        The Human Cost
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-8">
        Years Stolen
      </h2>

      <div ref={counterRef} className="flex flex-col items-center text-center mb-16">
        <div className="text-7xl md:text-9xl font-black text-rose-500">
          {isInView ? (
            <AnimatedCounter value={cost.total_extra_years} duration={3000} />
          ) : (
            <span>0</span>
          )}
        </div>
        <p className="text-xl text-white/60 mt-4 max-w-xl">
          extra years of imprisonment imposed on Black defendants beyond what
          White defendants received for the same offenses
        </p>
        <motion.p
          className="text-white/30 text-sm mt-2"
          initial={{ opacity: 0, y: 10 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
          transition={{ delay: 2.5, duration: 0.8 }}
        >
          That&apos;s {lifetimes} lifetimes.
        </motion.p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cost.by_offense.slice(0, 6).map(
          (o: { Offense: string; Extra_Years: number; N_Black: number; Black_Effect_Mo: number }, i: number) => (
            <motion.div
              key={o.Offense}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className="rounded-xl bg-slate-800/50 border border-white/5 p-6"
            >
              <p className="text-white/50 text-sm">{o.Offense}</p>
              <p className="text-3xl font-bold text-rose-500 mt-2">
                {o.Extra_Years.toLocaleString()} years
              </p>
              <p className="text-white/30 text-sm mt-1">
                +{o.Black_Effect_Mo} mo × {o.N_Black.toLocaleString()} defendants
              </p>
            </motion.div>
          )
        )}
      </div>
    </Section>
  );
}
