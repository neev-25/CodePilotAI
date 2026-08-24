import type { Metadata } from "next";
import { Architects_Daughter, Inter } from "next/font/google";
import "./globals.css";
import "reactflow/dist/style.css";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const architectsDaughter = Architects_Daughter({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-sketch",
  display: "swap",
});

export const metadata: Metadata = {
  title: "CodePilot AI — AI Developer Platform",
  description: "AI-powered GitHub repository analysis platform. Architecture, security, diagrams, review, and more — powered by Gemini.",
  keywords: ["AI", "code review", "GitHub", "repository analysis", "architecture diagram", "developer tools"],
  openGraph: {
    title: "CodePilot AI",
    description: "AI-powered GitHub repository analysis platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`h-full antialiased ${inter.variable} ${architectsDaughter.variable}`}>
      <body className="min-h-full flex flex-col font-sans">
        <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
