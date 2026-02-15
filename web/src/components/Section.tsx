"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

export default function Section({
  id,
  children,
  className = "",
  dark = true,
}: {
  id: string;
  children: ReactNode;
  className?: string;
  dark?: boolean;
}) {
  return (
    <section
      id={id}
      className={`relative px-6 py-16 md:py-24 ${
        dark ? "bg-slate-950" : "bg-slate-900"
      } ${className}`}
    >
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        viewport={{ once: true, margin: "-100px" }}
        className="mx-auto max-w-5xl"
      >
        {children}
      </motion.div>
    </section>
  );
}
