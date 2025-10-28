import { ReactNode } from 'react';
import { Inter } from "next/font/google";
import type { Metadata } from 'next';
import "./globals.css";
import { Providers } from "@/components/providers";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { GlobalErrorHandler } from "@/components/global-error-handler";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    default: 'UN Jobs Hub - Your Gateway to United Nations Careers',
    template: '%s | UN Jobs Hub'
  },
  description: 'Find and apply to UN jobs across 8+ organizations. AI-powered job matching, resume analysis, and personalized recommendations.',
  keywords: ['UN jobs', 'United Nations', 'international careers', 'WHO', 'UNICEF', 'UNDP', 'FAO', 'UNOPS', 'ILO'],
  authors: [{ name: 'UN Jobs Hub Team' }],
  creator: 'UN Jobs Hub',
  publisher: 'UN Jobs Hub',
  icons: {
    icon: [
      { url: '/icon.svg', type: 'image/svg+xml' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  },
  manifest: '/site.webmanifest',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://unjobshub.com',
    title: 'UN Jobs Hub - Your Gateway to United Nations Careers',
    description: 'Find and apply to UN jobs across 8+ organizations. AI-powered job matching.',
    siteName: 'UN Jobs Hub',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'UN Jobs Hub',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'UN Jobs Hub - Your Gateway to United Nations Careers',
    description: 'Find and apply to UN jobs across 8+ organizations. AI-powered job matching.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <GlobalErrorHandler />
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}
