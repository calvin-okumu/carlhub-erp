"use client";

import { ArrowUpRight, CalendarDays, CheckCircle2, ChevronDown, ChevronUp, Zap } from "lucide-react";
import { useState } from "react";

const priorities = [
    { label: "Finalize Q2 forecast", due: "Today", status: "In review" },
    { label: "Client renewal deck", due: "Tomorrow", status: "Draft" },
    { label: "Ops sync brief", due: "Friday", status: "Ready" },
];

const sessions = [
    { label: "Revenue standup", time: "09:30 AM" },
    { label: "Pipeline review", time: "01:00 PM" },
    { label: "People ops check-in", time: "04:15 PM" },
];

export default function DashboardFocusPanel() {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <aside className="rounded-[30px] border border-slate-200/70 bg-white/85 p-6 shadow-[0_26px_60px_-45px_rgba(15,23,42,0.6)]">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-600">
                        <Zap className="h-5 w-5" />
                    </div>
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Focus</p>
                        <h3 className="font-display text-lg font-semibold text-slate-900">Priority lane</h3>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="hidden rounded-full border border-emerald-200/70 bg-emerald-50 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-emerald-700 md:inline-flex">
                        Live
                    </span>
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
            <div className={`${isExpanded ? "block" : "hidden md:block"}`}>
                <div className="mt-5 space-y-4">
                    {priorities.map((item) => (
                        <div key={item.label} className="rounded-2xl border border-slate-200/70 bg-slate-50/80 p-4">
                            <div className="flex items-center justify-between text-sm font-semibold text-slate-700">
                                <span>{item.label}</span>
                                <span className="text-xs uppercase tracking-[0.2em] text-slate-400">{item.due}</span>
                            </div>
                            <div className="mt-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600">
                                <CheckCircle2 className="h-4 w-4" />
                                {item.status}
                            </div>
                        </div>
                    ))}
                </div>
                <div className="mt-6 rounded-2xl border border-slate-200/70 bg-slate-50/80 p-4">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900 text-white">
                            <CalendarDays className="h-4 w-4" />
                        </div>
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Schedule</p>
                            <h4 className="font-display text-base font-semibold text-slate-900">Next sessions</h4>
                        </div>
                    </div>
                    <div className="mt-4 space-y-3">
                        {sessions.map((item) => (
                            <div key={item.label} className="flex items-center justify-between rounded-2xl border border-slate-200/70 bg-white/80 px-4 py-3 text-sm">
                                <span className="font-medium text-slate-700">{item.label}</span>
                                <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{item.time}</span>
                            </div>
                        ))}
                    </div>
                </div>
                <button
                    type="button"
                    className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-white"
                >
                    Review tasks
                    <ArrowUpRight className="h-4 w-4" />
                </button>
            </div>
        </aside>
    );
}
