
"use client";

import { ArrowUpRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function Banner() {
    const [firstName, setFirstName] = useState("User");

    useEffect(() => {
        const user = localStorage.getItem("user");
        if (user) {
            const parsed = JSON.parse(user);
            const name = parsed.first_name || (parsed.email ? parsed.email.split("@")[0] : "User");
            setFirstName(name);
        }
    }, []);

    return (
        <section className="group relative overflow-hidden rounded-[30px] border border-slate-200/70 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.18),_transparent_52%),radial-gradient(circle_at_70%_0%,_rgba(251,146,60,0.18),_transparent_55%),linear-gradient(135deg,_rgba(255,255,255,0.96),_rgba(248,250,252,0.9))] p-6 shadow-[0_30px_70px_-50px_rgba(15,23,42,0.6)] md:p-8">
            <div className="absolute -right-24 -top-20 h-56 w-56 rounded-full bg-sky-200/40 blur-3xl transition-opacity duration-500 group-hover:opacity-90" />
            <div className="absolute -left-20 bottom-0 h-60 w-60 rounded-full bg-orange-200/35 blur-3xl transition-opacity duration-500 group-hover:opacity-90" />
            <div className="relative grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
                <div>
                    <div className="flex flex-wrap items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900/95 shadow-lg shadow-slate-900/15">
                            <Image src="/logo.png" alt="CarlHub Logo" width={28} height={28} className="h-7 w-7" />
                        </div>
                        <span className="inline-flex items-center rounded-full border border-slate-200/70 bg-white/80 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.35em] text-slate-500">
                            Orbit Console
                        </span>
                        <span className="inline-flex items-center rounded-full border border-slate-200/70 bg-white/80 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.32em] text-slate-500">
                            Wed Sync
                        </span>
                    </div>
                    <h1 className="font-display mt-5 text-2xl font-semibold tracking-tight text-slate-900 md:text-4xl lg:text-5xl">
                        Good to see you, {firstName}.
                    </h1>
                    <p className="mt-3 max-w-xl text-sm text-slate-600 md:text-base">
                        <span className="sm:hidden">Stay ahead of the workstream with a pulse-first view.</span>
                        <span className="hidden sm:inline">
                            The command deck is tuned for velocity. Scan the pulse, align the lanes, and drop into the workflows that need you most.
                        </span>
                    </p>
                    <div className="mt-5 flex flex-wrap items-center gap-3">
                        <Link
                            href="#apps"
                            className="inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-800"
                        >
                            Explore lanes
                        </Link>
                        <Link
                            href="/dashboard/crm/clients"
                            className="inline-flex items-center justify-center rounded-full border border-slate-200/70 bg-white/80 px-4 py-2.5 text-sm font-semibold text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-white"
                            aria-label="Open CRM"
                        >
                            <span className="hidden sm:inline">Open CRM</span>
                            <ArrowUpRight className="h-4 w-4 sm:ml-2" />
                        </Link>
                        <div className="flex items-center gap-2 rounded-full border border-emerald-200/70 bg-emerald-50 px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-emerald-700">
                            <span className="h-2 w-2 rounded-full bg-emerald-500" />
                            Live workspace
                        </div>
                    </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                    {[
                        { label: "Pipeline", value: "$218k", note: "7 deals in motion" },
                        { label: "Projects", value: "14", note: "3 with blockers" },
                        { label: "Tickets", value: "32", note: "5 escalated" },
                        { label: "People", value: "128", note: "Active seats" },
                    ].map((item) => (
                        <div
                            key={item.label}
                            className="rounded-[22px] border border-slate-200/70 bg-white/85 px-4 py-3 shadow-[0_18px_45px_-35px_rgba(15,23,42,0.5)]"
                        >
                            <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-400">{item.label}</p>
                            <div className="mt-2 flex items-center justify-between">
                                <p className="text-xl font-semibold text-slate-900">{item.value}</p>
                                <span className="rounded-full border border-slate-200/70 bg-slate-50 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                                    {item.note}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
