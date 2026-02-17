"use client";

import Section from "./Section";

const orgs = [
  { name: "The Sentencing Project", url: "https://www.sentencingproject.org" },
  { name: "ACLU Criminal Law Reform", url: "https://www.aclu.org/issues/smart-justice" },
  { name: "Vera Institute of Justice", url: "https://www.vera.org" },
  { name: "Equal Justice Initiative", url: "https://eji.org" },
  { name: "FAMM (Families Against Mandatory Minimums)", url: "https://famm.org" },
];

export default function TakeAction() {
  const shareUrl = "https://samecrimedifferenttime.org";
  const shareText = "Black defendants get 3.85 months longer for the same crime. 1.3M federal sentences exposed. samecrimedifferenttime.org via @Justice_Index";

  return (
    <Section id="action" dark={false}>
      <p className="text-sm uppercase tracking-[0.2em] text-rose-400/70 mb-2">
        Take Action
      </p>
      <h2 className="text-4xl font-bold md:text-5xl mb-4">
        What You Can Do
      </h2>
      <p className="text-white/50 max-w-2xl mb-10">
        Data alone doesn&apos;t change policy. People do.
      </p>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="rounded-xl bg-slate-800/50 border border-white/5 p-8">
          <h3 className="text-xl font-bold mb-4">📣 Share This Research</h3>
          <div className="flex flex-wrap gap-3">
            <a
              href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm transition-colors"
            >
              Share on X
            </a>
            <a
              href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm transition-colors"
            >
              Share on Facebook
            </a>
            <a
              href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm transition-colors"
            >
              Share on LinkedIn
            </a>
            <a
              href={`https://www.tiktok.com/`}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => { e.preventDefault(); navigator.clipboard.writeText(`${shareText} ${shareUrl}`); alert("Link copied! Paste it into your TikTok caption."); }}
              className="rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm transition-colors"
            >
              Share on TikTok
            </a>
            <a
              href="#"
              onClick={(e) => { e.preventDefault(); navigator.clipboard.writeText(`${shareText} ${shareUrl}`); alert("Link copied! Paste it into your Instagram story or caption."); }}
              className="rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm transition-colors"
            >
              Share on Instagram
            </a>
            <a
              href={`https://www.snapchat.com/scan?attachmentUrl=${encodeURIComponent(shareUrl)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm transition-colors"
            >
              Share on Snapchat
            </a>
            <a
              href="#"
              onClick={(e) => { e.preventDefault(); navigator.clipboard.writeText(shareUrl); alert("Link copied to clipboard!"); }}
              className="rounded-lg bg-slate-700 hover:bg-slate-600 px-4 py-2 text-sm transition-colors"
            >
              📋 Copy Link
            </a>
          </div>
        </div>

        <div className="rounded-xl bg-slate-800/50 border border-white/5 p-8">
          <h3 className="text-xl font-bold mb-4">🏛️ Contact Your Representatives</h3>
          <p className="text-white/50 text-sm mb-4">
            Federal sentencing reform starts in Congress.
          </p>
          <a
            href="https://www.senate.gov/senators/senators-contact.htm"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg bg-rose-600 hover:bg-rose-500 px-6 py-3 text-sm font-bold inline-block transition-colors"
          >
            Find Your Senator →
          </a>
        </div>
      </div>

      {/* Follow CTA */}
      <div className="rounded-xl bg-slate-800/50 border border-white/5 p-8 mb-12 text-center">
        <h3 className="text-xl font-bold mb-2">Follow @Justice_Index for updates</h3>
        <p className="text-white/50 text-sm mb-6">New investigations, data updates, and analysis.</p>
        <div className="flex flex-wrap justify-center gap-3">
          <a
            href="https://x.com/Justice_Index"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-white/10 hover:bg-white/20 px-5 py-2.5 text-sm font-medium text-white transition"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            @Justice_Index on X
          </a>
          <a
            href="https://instagram.com/justiceindex"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-white/10 hover:bg-white/20 px-5 py-2.5 text-sm font-medium text-white transition"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
            @justiceindex on Instagram
          </a>
        </div>
      </div>

      <h3 className="text-xl font-bold mb-6">Organizations Working on Reform</h3>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {orgs.map((org) => (
          <a
            key={org.name}
            href={org.url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-xl bg-slate-800/30 border border-white/5 p-5 hover:border-white/20 transition-colors"
          >
            <p className="font-semibold">{org.name}</p>
            <p className="text-white/30 text-sm mt-1">{org.url.replace("https://", "")}</p>
          </a>
        ))}
      </div>
    </Section>
  );
}
