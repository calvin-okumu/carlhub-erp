"use client";

import {
    Activity,
    ArrowUpRight,
    ChevronDown,
    ChevronUp,
    Flag,
    Radar,
    Sparkles,
    Target,
} from "lucide-react";
import { useState } from "react";

const signals = [
    {
        title: "Revenue glidepath",
        value: "$284k",
        delta: "+12.4%",
        detail: "Forecast for 30 days",
        icon: Target,
        accent: "text-emerald-600",
        ring: "ring-emerald-200/70",
        glow: "from-emerald-500/15 via-emerald-500/0",
    },
    {
        title: "Team bandwidth",
        value: "78%",
        delta: "Stable",
        detail: "Capacity utilization",
        icon: Activity,
        accent: "text-amber-600",
        ring: "ring-amber-200/70",
        glow: "from-amber-500/15 via-amber-500/0",
    },
    {
        title: "Client health",
        value: "92%",
        delta: "+4%",
        detail: "Healthy accounts",
        icon: Sparkles,
        accent: "text-sky-600",
        ring: "ring-sky-200/70",
        glow: "from-sky-500/15 via-sky-500/0",
    },
];

const runway = [
    {
        label: "New contracts in review",
        progress: 64,
        status: "3 this week",
    },
    {
        label: "Onboarding sequences",
        progress: 42,
        status: "5 active",
    },
    {
        label: "Operations automation",
        progress: 78,
        status: "2 wins shipped",
    },
];

export default function DashboardSignals() {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <section className="rounded-[30px] border border-slate-200/70 bg-white/85 p-6 shadow-[0_26px_60px_-45px_rgba(15,23,42,0.55)]">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">Signals</p>
                    <h3 className="font-display mt-2 text-xl font-semibold text-slate-900">Operations snapshot</h3>
                </div>
                <div className="flex items-center gap-2">
                    <div className="hidden items-center gap-2 rounded-full border border-slate-200/70 bg-white/80 px-3 py-1 text-xs font-semibold text-slate-600 md:flex">
                        <Radar className="h-3.5 w-3.5" />
                        Live sync
                    </div>
                    <button
                        type="button"
                        onClick={() => setIsExpanded((prev) => !prev)}
                        className="inline-flex items-center gap-1 rounded-full border border-slate-200/70 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500 md:hidden"
                    >
                        {isExpanded ? "Hide" : "Show"}
                        {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                    </button>
                </div>
            </div>
            <div className={`mt-5 space-y-4 ${isExpanded ? "block" : "hidden md:block"}`}>
                <div className="grid gap-4 md:grid-cols-3">
                {signals.map((signal) => (
                    <div
                        key={signal.title}
                        className="relative overflow-hidden rounded-2xl border border-slate-200/70 bg-white/90 p-4"
                    >
                        <div className={`absolute inset-0 bg-gradient-to-br ${signal.glow} to-transparent`} />
                        <div className="relative">
                            <div className="flex items-center justify-between">
                                <div className={`flex h-10 w-10 items-center justify-center rounded-2xl bg-white ring-1 ${signal.ring} shadow-sm`}>
                                    <signal.icon className={`h-5 w-5 ${signal.accent}`} />
                                </div>
                                <span className={`text-[10px] font-semibold uppercase tracking-[0.2em] ${signal.accent}`}>
                                    {signal.delta}
                                </span>
                            </div>
                            <p className="mt-3 text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-400">
                                {signal.title}
                            </p>
                            <p className="font-display mt-1 text-xl font-semibold text-slate-900">
                                {signal.value}
                            </p>
                            <p className="mt-1 text-xs text-slate-600">{signal.detail}</p>
                        </div>
                    </div>
                ))}
                </div>
                <div className="rounded-2xl border border-slate-200/60 bg-slate-50/80 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                        Runway snapshot
                    </p>
                    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        <Flag className="h-3.5 w-3.5" />
                        Ops review in 2 days
                    </div>
                </div>
                <div className="mt-4 space-y-3">
                    {runway.map((item) => (
                        <div key={item.label} className="rounded-xl border border-slate-200/60 bg-white/90 p-3">
                            <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                                <span>{item.label}</span>
                                <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                                    {item.status}
                                </span>
                            </div>
                            <div className="mt-2 h-2 w-full rounded-full bg-slate-200/60">
                                <div
                                    className="h-2 rounded-full bg-gradient-to-r from-slate-900 via-slate-700 to-slate-500"
                                    style={{ width: `${item.progress}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
                <button
                    type="button"
                    className="mt-4 inline-flex items-center gap-2 rounded-full border border-slate-200/70 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600"
                >
                    Export signal report
                    <ArrowUpRight className="h-3.5 w-3.5" />
                </button>
                </div>
            </div>
        </section>
    );
}
