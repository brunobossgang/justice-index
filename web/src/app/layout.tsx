import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Same Crime. Different Time. | Justice Index",
  description:
    "Analysis of 1.3 million federal sentences reveals Black defendants receive 3.85 months longer for the same crime.",
  metadataBase: new URL("https://samecrimedifferenttime.org"),
  alternates: {
    canonical: "/",
  },
  authors: [{ name: "Bruno Beckman" }],
  openGraph: {
    title: "Same Crime, Different Time: Racial Disparities in Federal Sentencing",
    description:
      "Analysis of 1.3 million federal sentences reveals Black defendants receive 3.85 months longer for the same crime.",
    url: "https://samecrimedifferenttime.org",
    type: "article",
    publishedTime: "2026-02-14T00:00:00Z",
    authors: ["Bruno Beckman"],
    images: [
      {
        url: "https://samecrimedifferenttime.org/og.png",
        width: 1200,
        height: 630,
        alt: "Same Crime, Different Time — +3.85 months longer sentences",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Same Crime. Different Time. | Justice Index",
    description:
      "Black defendants receive +3.85 months longer sentences. 1.3M cases, 23 years of USSC data.",
    images: ["https://samecrimedifferenttime.org/og.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify([
              {
                "@context": "https://schema.org",
                "@type": "Article",
                headline: "Same Crime, Different Time: Racial Disparities in Federal Sentencing",
                description:
                  "Analysis of 1.3 million federal sentences reveals Black defendants receive 3.85 months longer for the same crime.",
                author: { "@type": "Person", name: "Bruno Beckman" },
                datePublished: "2026-02-14",
                publisher: { "@type": "Organization", name: "Justice Index", url: "https://justice-index.org" },
                mainEntityOfPage: "https://samecrimedifferenttime.org",
                image: "https://samecrimedifferenttime.org/og.png",
              },
              {
                "@context": "https://schema.org",
                "@type": "Dataset",
                name: "Federal Sentencing Records FY2002-2024",
                description: "1,294,673 federal sentencing records from the U.S. Sentencing Commission, FY2002-2024.",
                url: "https://samecrimedifferenttime.org",
                creator: { "@type": "Person", name: "Bruno Beckman" },
              },
            ]),
          }}
        />
      </head>
      <body className={`${inter.className} bg-slate-950 text-white antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
