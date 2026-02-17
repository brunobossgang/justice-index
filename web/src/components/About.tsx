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

        {/* Cross-link banner */}
        <div className="mt-12 bg-gradient-to-r from-rose-500/10 to-amber-500/10 border border-rose-500/20 rounded-2xl p-6">
          <p className="text-sm font-medium uppercase tracking-wider text-rose-400/80 mb-2">
            Justice Index · Three Investigations
          </p>
          <p className="text-white/70">
            Bias doesn&apos;t stop at sentencing. It follows people from the traffic stop
            to the courtroom to the bank.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <a
              href="https://samestopdifferentoutcome.org"
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-xl text-rose-400 hover:text-rose-300 text-sm font-semibold transition-colors"
            >
              Same Stop, Different Outcome → Traffic Stops
            </a>
            <a
              href="https://sameloandifferentrate.org"
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-xl text-rose-400 hover:text-rose-300 text-sm font-semibold transition-colors"
            >
              Same Loan, Different Rate → Mortgage Lending
            </a>
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-white/5 text-center text-white/30 text-sm">
          <div className="flex flex-wrap justify-center gap-4 mb-3">
            <a href="https://justice-index.org" className="hover:text-white/50 transition">Justice Index</a>
            <a href="https://samestopdifferentoutcome.org" className="hover:text-white/50 transition">Same Stop</a>
            <a href="https://sameloandifferentrate.org" className="hover:text-white/50 transition">Same Loan</a>
            <a href="https://github.com/brunobossgang/justice-index" target="_blank" rel="noopener noreferrer" className="hover:text-white/50 transition">GitHub</a>
          </div>
          <div className="flex flex-wrap justify-center gap-6 mt-2">
            <a href="https://x.com/Justice_Index" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 hover:text-white/50 transition">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              @Justice_Index on Twitter
            </a>
            <a href="https://instagram.com/justiceindex" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 hover:text-white/50 transition">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
              @justiceindex on Instagram
            </a>
          </div>
          <p>© 2026 Justice Index</p>
        </div>
      </div>
    </footer>
  );
}
