import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Same Crime. Different Time. | Justice Index",
  description:
    "23 years of federal sentencing data expose persistent racial disparities in the US criminal justice system. 1.3 million cases. The numbers speak for themselves.",
  openGraph: {
    title: "Same Crime. Different Time.",
    description:
      "Black defendants receive nearly 4 extra months in federal prison — even after controlling for offense, criminal history, and other factors.",
    url: "https://samecrimedifferenttime.org",
    type: "website",
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
      </head>
      <body className={`${inter.className} bg-slate-950 text-white antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
