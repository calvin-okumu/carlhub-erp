
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
        <div className="min-h-screen bg-[radial-gradient(1200px_circle_at_12%_-10%,rgba(59,130,246,0.16),transparent_55%),radial-gradient(900px_circle_at_90%_-5%,rgba(251,146,60,0.14),transparent_55%),linear-gradient(150deg,rgba(248,250,252,0.96)_0%,rgba(255,255,255,0.92)_50%,rgba(241,245,249,0.92)_100%)]">
            <header className="border-b border-slate-200/70 bg-white/75 px-4 py-4 backdrop-blur">
                <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between">
                    <Link href="/" className="flex items-center gap-3">
                        <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900/95 shadow-lg shadow-slate-900/15">
                            <Image
                                src="/logo.png"
                                alt="Carlhub Logo"
                                width={22}
                                height={22}
                            />
                        </span>
                        <span className="font-display text-lg font-semibold tracking-tight text-slate-900">
                            Carlhub
                        </span>
                    </Link>
                    <span className="hidden rounded-full border border-slate-200/70 bg-white/80 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.3em] text-slate-500 sm:inline-flex">
                        Secure access
                    </span>
                </div>
            </header>

            <main className="mx-auto grid w-full max-w-[1200px] gap-10 px-4 py-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
                <div className="hidden rounded-[30px] border border-slate-200/70 bg-white/80 p-8 shadow-[0_30px_70px_-50px_rgba(15,23,42,0.6)] lg:block">
                    <div className="flex items-center gap-3">
                        <span className="rounded-full border border-slate-200/70 bg-white/80 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.3em] text-slate-500">
                            Workspace access
                        </span>
                        <span className="rounded-full border border-emerald-200/70 bg-emerald-50 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-emerald-700">
                            Live
                        </span>
                    </div>
                    <h2 className="font-display mt-4 text-3xl font-semibold text-slate-900">
                        Operate your workspace with a calmer command view.
                    </h2>
                    <p className="mt-3 text-sm text-slate-600">
                        Stay aligned across projects, client health, and team delivery. Your command center is tuned for focus and clarity.
                    </p>
                    <div className="mt-6 rounded-[24px] border border-slate-200/70 bg-white/90 p-4">
                        <Image
                            src="/bg.png"
                            alt="Authentication Illustration"
                            width={640}
                            height={520}
                            priority
                            className="rounded-[18px]"
                        />
                    </div>
                </div>

                <div className="rounded-[30px] border border-slate-200/70 bg-white/90 p-8 shadow-[0_30px_70px_-50px_rgba(15,23,42,0.6)]">
                    {title && <h2 className="font-display text-2xl font-semibold text-slate-900">{title}</h2>}
                    {subtitle && <p className="mt-2 text-sm text-slate-600">{subtitle}</p>}
                    {children}
                </div>
            </main>
        </div>
    );
}
