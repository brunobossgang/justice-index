"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Section from "./Section";
import data from "@/data/precomputed.json";

const params = data.model_params as Record<string, number>;

const OFFENSE_MAP: Record<string, string> = {
  "Administration of Justice": "off_1",
  "Kidnapping": "off_4",
  "Environmental": "off_5",
  "Firearms": "off_7",
  "Fraud/Theft/Embezzlement": "off_13",
  "Immigration": "off_16",
  "Individual Rights": "off_17",
  "Drug Possession": "off_21",
  "Drug Trafficking": "off_22",
  "Robbery": "off_26",
  "Obscenity/Sex Offenses": "off_27",
  "Tax": "off_30",
  "Other": "",
};

const RACE_CONFIG = [
  { key: "White", isBlack: false, isHispanic: false, color: "#94a3b8", label: "If White" },
  { key: "Black", isBlack: true, isHispanic: false, color: "#f43f5e", label: "If Black" },
  { key: "Hispanic", isBlack: false, isHispanic: true, color: "#f59e0b", label: "If Hispanic" },
];

export default function Calculator() {
  const [gender, setGender] = useState("Male");
  const [offense, setOffense] = useState("Drug Trafficking");
  const [guidelineMin, setGuidelineMin] = useState(60);
  const [crimPts, setCrimPts] = useState(3);
  const [age, setAge] = useState(35);
  const [weapon, setWeapon] = useState(false);
  const [results, setResults] = useState<{ white: number; black: number; hispanic: number } | null>(null);

  const predict = (isBlack: boolean, isHispanic: boolean) => {
    let val = params.const || 0;
    if (isBlack) val += params.Black || 0;
    if (isHispanic) val += params.Hispanic || 0;
    if (gender === "Female") val += params.Female || 0;
    val += (params.XMINSOR || 0) * guidelineMin;
    val += (params.CRIMPTS || 0) * crimPts;
    val += (params.AGE || 0) * age;
    if (weapon) val += params.WEAPON || 0;
    const offKey = OFFENSE_MAP[offense];
    if (offKey && params[offKey]) val += params[offKey];
    return Math.max(0, val);
  };

  const calculate = () => {
    setResults({
      white: predict(false, false),
      black: predict(true, false),
      hispanic: predict(false, true),
    });
  };

  const resultValues = results ? [
    { ...RACE_CONFIG[0], value: results.white },
    { ...RACE_CONFIG[1], value: results.black },
    { ...RACE_CONFIG[2], value: results.hispanic },
  ] : null;

  return (
    <Section id="calculator">
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        The Calculator
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-4">
        What Would Your Sentence Be?
      </h2>
      <p className="text-white/50 max-w-2xl mb-10">
        Pick everything except race. Then see how race alone changes the outcome.
      </p>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div>
          <label className="block text-sm text-white/60 mb-2">Gender</label>
          <select value={gender} onChange={(e) => setGender(e.target.value)}
            className="w-full rounded-lg border border-white/10 bg-slate-800 px-4 py-3 text-white">
            <option>Male</option>
            <option>Female</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-white/60 mb-2">Offense</label>
          <select value={offense} onChange={(e) => setOffense(e.target.value)}
            className="w-full rounded-lg border border-white/10 bg-slate-800 px-4 py-3 text-white">
            {Object.keys(OFFENSE_MAP).map((o) => (
              <option key={o}>{o}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-white/60 mb-2">
            Guideline Minimum (months): {guidelineMin}
          </label>
          <input type="range" min={0} max={240} value={guidelineMin}
            onChange={(e) => setGuidelineMin(Number(e.target.value))}
            className="w-full accent-rose-500" />
        </div>
        <div>
          <label className="block text-sm text-white/60 mb-2">
            Criminal History Points: {crimPts}
          </label>
          <input type="range" min={0} max={20} value={crimPts}
            onChange={(e) => setCrimPts(Number(e.target.value))}
            className="w-full accent-rose-500" />
        </div>
        <div>
          <label className="block text-sm text-white/60 mb-2">Age: {age}</label>
          <input type="range" min={18} max={80} value={age}
            onChange={(e) => setAge(Number(e.target.value))}
            className="w-full accent-rose-500" />
        </div>
        <div className="flex items-center gap-3">
          <input type="checkbox" checked={weapon}
            onChange={(e) => setWeapon(e.target.checked)}
            className="h-5 w-5 accent-rose-500" />
          <label className="text-white/60">Weapon involved</label>
        </div>
      </div>

      <button
        onClick={calculate}
        className="rounded-xl bg-rose-600 hover:bg-rose-500 px-8 py-4 text-lg font-bold transition-colors"
      >
        Calculate Predicted Sentence
      </button>

      <AnimatePresence>
        {resultValues && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-10"
          >
            <p className="text-center text-lg text-white/40 mb-6 italic">
              Same person. Same crime. Different sentence.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {resultValues.map((r) => {
                const diff = r.value - resultValues[0].value;
                return (
                  <motion.div
                    key={r.key}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: r.isBlack ? 0.2 : r.isHispanic ? 0.4 : 0 }}
                    className="rounded-xl border p-8 text-center"
                    style={{
                      borderColor: r.color + "40",
                      backgroundColor: r.color + "10",
                    }}
                  >
                    <p className="text-white/50 text-sm mb-3">{r.label}</p>
                    <p className="text-5xl font-black" style={{ color: r.color }}>
                      {r.value.toFixed(1)}
                    </p>
                    <p className="text-white/40 mt-1">months</p>
                    {diff !== 0 && (
                      <p className="mt-3 font-bold text-rose-400 text-sm">
                        {diff > 0 ? "+" : ""}{diff.toFixed(1)} months vs White
                      </p>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Section>
  );
}
