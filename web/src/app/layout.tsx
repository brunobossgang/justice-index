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
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} bg-slate-950 text-white antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
