import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "ReviewPilot Demo",
  description: "Demo Next.js app with intentional UX bugs for ReviewPilot to detect.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-slate-900 antialiased">
        <Navbar />
        {children}
        <Footer />
      </body>
    </html>
  );
}
