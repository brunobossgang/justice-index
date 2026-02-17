"use client";

import Section from "./Section";
import data from "@/data/precomputed";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
} from "recharts";

const yearly = data.yearly;

export default function Trend() {
  return (
    <Section id="trend">
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        The Trend
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-4">
        22 Years. Still Unequal.
      </h2>
      <p className="text-white/50 max-w-2xl mb-10">
        The Black penalty has persisted every single year since 2002.
        After briefly narrowing around 2015-2016, it has rebounded to over 5 months.
        The Hispanic effect (amber) fluctuates near zero — sometimes slightly above, sometimes below —
        telling a fundamentally different story from the persistent Black penalty.
      </p>

      <div className="w-full h-[400px] md:h-[500px]">
        <ResponsiveContainer>
          <LineChart data={yearly} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="Year"
              stroke="#64748b"
              tick={{ fill: "#94a3b8", fontSize: 12 }}
            />
            <YAxis
              stroke="#64748b"
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              label={{
                value: "Extra months",
                angle: -90,
                position: "insideLeft",
                fill: "#94a3b8",
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
              }}
            />
            <Legend />
            {/* Presidential era bands */}
            <ReferenceArea x1={2002} x2={2008} fill="#3b82f6" fillOpacity={0.08} label={{ value: "Bush", position: "insideTopLeft", fill: "#94a3b8", fontSize: 13, fontWeight: 600 }} />
            <ReferenceArea x1={2009} x2={2016} fill="#3b82f6" fillOpacity={0.08} label={{ value: "Obama", position: "insideTopLeft", fill: "#94a3b8", fontSize: 13, fontWeight: 600 }} />
            <ReferenceArea x1={2017} x2={2020} fill="#ef4444" fillOpacity={0.08} label={{ value: "Trump", position: "insideTopLeft", fill: "#94a3b8", fontSize: 13, fontWeight: 600 }} />
            <ReferenceArea x1={2021} x2={2024} fill="#3b82f6" fillOpacity={0.08} label={{ value: "Biden", position: "insideTopLeft", fill: "#94a3b8", fontSize: 13, fontWeight: 600 }} />
            <ReferenceLine y={0} stroke="#475569" strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="Black_Effect"
              name="Black penalty (months)"
              stroke="#f43f5e"
              strokeWidth={3}
              dot={{ r: 3, fill: "#f43f5e" }}
            />
            <Line
              type="monotone"
              dataKey="Hispanic_Effect"
              name="Hispanic effect (months)"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ r: 2, fill: "#f59e0b" }}
            />
            <Line
              type="monotone"
              dataKey="Female_Effect"
              name="Female effect (months)"
              stroke="#22d3ee"
              strokeWidth={2}
              dot={{ r: 2, fill: "#22d3ee" }}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Section>
  );
}
