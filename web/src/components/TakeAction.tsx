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
  const shareText = "Same Crime. Different Time. Black defendants get +3.85 months in federal prison — even after controlling for all legal factors.";

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
