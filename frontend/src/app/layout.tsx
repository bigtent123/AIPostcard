import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Postcard Search - Find Vintage Postcards Across Multiple Marketplaces",
  description: "Search for vintage postcards across eBay, Etsy, and HipPostcard with AI-enhanced search capabilities.",
  keywords: "postcards, vintage postcards, postcard search, collectible postcards, deltiology",
  openGraph: {
    title: "Postcard Search - Find Vintage Postcards",
    description: "Search for vintage postcards across multiple marketplaces with AI-enhanced search capabilities.",
    url: "https://postcard-search.netlify.app",
    siteName: "Postcard Search",
    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Postcard Search",
      },
    ],
    locale: "en_US",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          <header className="bg-white dark:bg-slate-900 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex justify-between items-center">
                <a href="/" className="flex items-center">
                  <span className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">Postcard Search</span>
                </a>
              </div>
            </div>
          </header>
          <main className="flex-grow">
            {children}
          </main>
          <footer className="bg-white dark:bg-slate-900 border-t border-gray-200 dark:border-gray-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <p className="text-center text-sm text-gray-500">
                © {new Date().getFullYear()} Postcard Search. All rights reserved.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
