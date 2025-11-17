"use client";

import Image from "next/image";
import Link from "next/link";
import { ReactNode } from "react";

interface AuthLayoutProps {
    children: ReactNode;
    title?: string;
    subtitle?: string;
}

export default function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
    return (
        <div className="min-h-screen flex flex-col bg-gray-50">
            {/* Header */}
            <header className="flex items-center p-4 bg-white shadow-sm">
                <Link href="/" className="flex items-center">
                    <Image
                        src="/logo.png"
                        alt="Carlhub Logo"
                        width={32}
                        height={32}
                        className="mr-2"
                    />
                    <h1 className="text-xl font-bold text-blue-600">Carlhub</h1>
                </Link>
            </header>

            {/* Main */}
            <main className="flex flex-1">
                {/* Left illustration - Full hero image */}
                <div className="hidden md:block relative w-1/2">
                    <Image
                        src="/bg.png"
                        alt="Authentication Illustration"
                        fill
                        priority
                        className="object-cover"
                    />

                    {/* Gradient overlay for style */}
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-700/10 to-white/40" />
                </div>

                {/* Right form */}
                <div className="flex flex-1 items-center justify-center p-10 bg-white">
                    <div className="w-full max-w-md">
                        {title && <h2 className="text-3xl font-semibold mb-2">{title}</h2>}
                        {subtitle && <p className="text-gray-500 mb-6">{subtitle}</p>}
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
}
