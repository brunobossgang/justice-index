"use client";

import data from "@/data/precomputed";

export default function About() {
  return (
    <footer id="about" className="bg-slate-900 border-t border-white/5 px-6 py-24">
      <div className="mx-auto max-w-5xl">
        <h2 className="text-2xl font-bold mb-8">About & Methodology</h2>

        <div className="grid md:grid-cols-2 gap-12 text-white/60 text-sm leading-relaxed">
          <div>
            <h3 className="text-white font-semibold mb-3">Data Source</h3>
            <p>
              All data comes from the{" "}
              <a
                href="https://www.ussc.gov/research/datafiles/commission-datafiles"
                target="_blank"
                rel="noopener noreferrer"
                className="text-rose-400 hover:text-rose-300 underline"
              >
                U.S. Sentencing Commission
              </a>{" "}
              Individual Offender Datafiles, fiscal years {data.summary.year_min}–
              {data.summary.year_max}. Total cases analyzed:{" "}
              {data.summary.total_cases.toLocaleString()}.
            </p>

            <h3 className="text-white font-semibold mt-6 mb-3">Methodology</h3>
            <p>
              We use Ordinary Least Squares (OLS) regression with sentence length in months
              as the dependent variable. Controls include: guideline minimum sentence,
              criminal history points, age, citizenship status, weapon involvement, and
              offense type dummies. The model achieves R² = {data.overall.r_squared.toFixed(4)},
              explaining {(data.overall.r_squared * 100).toFixed(1)}% of sentence variation.
            </p>
            <p className="mt-3">
              The racial disparity coefficient represents the additional months of
              imprisonment associated with being Black vs. White, after controlling
              for all included legal and demographic factors.
            </p>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-3">Limitations</h3>
            <p>
              Observational data cannot prove causation. Unobserved variables (e.g.,
              quality of legal representation, plea bargaining dynamics) may influence
              results. The model controls for available legal factors but cannot account
              for all possible confounders.
            </p>

            <h3 className="text-white font-semibold mt-6 mb-3">Open Source</h3>
            <p>
              All code, data processing, and analysis are open source.
            </p>
            <a
              href="https://github.com/brunobossgang/justice-index"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-3 rounded-lg bg-slate-800 hover:bg-slate-700 px-4 py-2 text-white/80 transition-colors"
            >
              GitHub → brunobossgang/justice-index
            </a>

            <h3 className="text-white font-semibold mt-6 mb-3">Citation</h3>
            <p className="font-mono text-xs text-white/40">
              Justice Index. &quot;Same Crime, Different Time: Racial Disparities in Federal
              Sentencing, {data.summary.year_min}–{data.summary.year_max}.&quot;
              samecrimedifferenttime.org, 2026.
            </p>
          </div>
        </div>

        {/* Cross-link to Same Stop */}
        <div className="mt-12 bg-gradient-to-r from-rose-500/10 to-amber-500/10 border border-rose-500/20 rounded-2xl p-6">
          <p className="text-sm font-medium uppercase tracking-wider text-rose-400/80 mb-2">
            Justice Index · Traffic Stops
          </p>
          <p className="text-white/70">
            Sentencing is just one piece. The bias starts long before the courtroom — 
            at the traffic stop. We analyzed 6.5 million stops across 13 states.
          </p>
          <a
            href="https://samestopdifferentoutcome.org"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-xl text-rose-400 hover:text-rose-300 text-sm font-semibold transition-colors"
          >
            Same Stop, Different Outcome → Racial Bias in Traffic Stops
          </a>
        </div>

        <div className="mt-16 pt-8 border-t border-white/5 text-center text-white/30 text-sm">
          <p>
            © 2026 Justice Index · samecrimedifferenttime.org ·{" "}
            <a href="https://github.com/brunobossgang/justice-index" className="hover:text-white/50">
              GitHub
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}
