import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: 'AI Pulse — Latest AI News and Updates',
  description: 'Daily AI updates from Anthropic, OpenAI, Google DeepMind and more. Curated and summarized for you.',
  keywords: 'AI news, artificial intelligence, Anthropic, OpenAI, Google DeepMind, machine learning',
  openGraph: {
    title: 'AI Pulse — Latest AI News and Updates',
    description: 'Daily AI updates curated by AI, reviewed by humans.',
    url: 'https://ai-news-site-pi.vercel.app',
    siteName: 'AI Pulse',
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
