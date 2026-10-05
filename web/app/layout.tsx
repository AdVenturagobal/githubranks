import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const grotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-disp" });
const plex = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-mono" });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.SITE_URL ?? "https://gitrise.pages.dev"),
  title: { default: "GitRise — See what's actually rising on GitHub", template: "%s · GitRise" },
  description:
    "Daily, weekly and monthly GitHub rankings by real net star growth, per field, in English and Chinese. Transparent numbers, full history.",
  openGraph: {
    siteName: "GitRise",
    images: [{ url: "/og.png", width: 1200, height: 630 }],
  },
  twitter: { card: "summary_large_image" },
  alternates: { types: { "application/rss+xml": "/feed.xml" } },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${grotesk.variable} ${plex.variable}`}>
      <body>{children}</body>
    </html>
  );
}
