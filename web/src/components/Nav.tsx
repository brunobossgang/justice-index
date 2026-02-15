"use client";

import { useState } from "react";

const links = [
  { href: "#human-cost", label: "Human Cost" },
  { href: "#comparison", label: "Disparity" },
  { href: "#trend", label: "Trend" },
  { href: "#map", label: "Map" },
  { href: "#calculator", label: "Calculator" },
  { href: "#evidence", label: "Evidence" },
  { href: "#action", label: "Act" },
];

export default function Nav() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 z-50 w-full bg-slate-950/80 backdrop-blur-md border-b border-white/5">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <a href="#" className="text-sm font-bold tracking-wider text-white/90">
          JUSTICE INDEX
        </a>
        <button
          className="md:hidden text-white/70"
          onClick={() => setOpen(!open)}
        >
          ☰
        </button>
        <div className={`${open ? "flex" : "hidden"} md:flex gap-6 absolute md:static top-full left-0 w-full md:w-auto bg-slate-950/95 md:bg-transparent px-6 py-4 md:p-0 flex-col md:flex-row`}>
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="text-sm text-white/60 hover:text-white transition-colors"
            >
              {l.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}
