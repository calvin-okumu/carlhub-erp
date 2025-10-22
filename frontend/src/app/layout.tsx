import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Carlhub",
  description: "Intelligent Business Management",
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
