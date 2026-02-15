"use client";

import { useState } from "react";
import Section from "./Section";
import data from "@/data/precomputed.json";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const lottery = data.lottery as Record<
  string,
  { districts: Array<{ district_name: string; avg: number; med: number; n: number }> }
>;
const offenses = Object.keys(lottery);

export default function MapSection() {
  const [offense, setOffense] = useState(offenses[0]);
  const districts = lottery[offense]?.districts || [];

  // Top 20 and bottom 10 by avg sentence
  const sorted = [...districts].sort((a, b) => b.avg - a.avg);
  const top = sorted.slice(0, 15);
  const bottom = sorted.slice(-10).reverse();
  const combined = [...top, ...bottom];
  const medianAvg = sorted.length > 0 ? sorted[Math.floor(sorted.length / 2)].avg : 0;

  return (
    <Section id="map" dark={false}>
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        The Geographic Lottery
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-4">
        Where You&apos;re Sentenced Matters
      </h2>
      <p className="text-white/50 max-w-2xl mb-10">
        Average sentence length varies dramatically across federal districts.
        Your zip code can mean the difference between years behind bars.
      </p>

      <select
        value={offense}
        onChange={(e) => setOffense(e.target.value)}
        className="mb-8 rounded-lg border border-white/10 bg-slate-800 px-4 py-3 text-white w-full max-w-xs"
      >
        {offenses.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>

      <div className="w-full h-[600px]">
        <ResponsiveContainer>
          <BarChart data={combined} layout="vertical" margin={{ left: 120, right: 30 }}>
            <XAxis
              type="number"
              stroke="#64748b"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              label={{ value: "Avg sentence (months)", position: "bottom", fill: "#94a3b8" }}
            />
            <YAxis
              type="category"
              dataKey="district_name"
              stroke="#64748b"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              width={110}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
              }}
              formatter={(value: number | undefined) => [`${(value ?? 0).toFixed(1)} months`, "Avg sentence"]}
            />
            <Bar dataKey="avg" radius={[0, 4, 4, 0]}>
              {combined.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.avg > medianAvg ? "#f43f5e" : "#0ea5e9"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="text-white/40 text-sm mt-4">
        <span className="text-rose-500">■</span> Above median &nbsp;
        <span className="text-sky-500">■</span> Below median
      </p>
    </Section>
  );
}
