
import React from "react";
import Card from "@/components/ui/Card";

interface ProjectProgressProps {
    overall: number;
    milestoneAverage: number;
}

const clampValue = (value: number) => Math.min(Math.max(Math.round(value), 0), 100);

export default function ProjectProgress({
    overall,
    milestoneAverage,
}: ProjectProgressProps) {
    const safeOverall = clampValue(overall);
    const safeMilestones = clampValue(milestoneAverage);

    const bars = [
        {
            label: "Delivery progress",
            value: safeOverall,
            helper: "Overall completion",
            color: "bg-emerald-500",
            track: "bg-emerald-100",
        },
        {
            label: "Milestone average",
            value: safeMilestones,
            helper: "Across active milestones",
            color: "bg-sky-500",
            track: "bg-sky-100",
        },
    ];

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !bg-white/90 !shadow-sm p-4 text-slate-900">
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Progress</p>
                    <h2 className="mt-2 text-xl font-semibold text-slate-900">Project Performance</h2>
                    <p className="mt-1 text-sm text-slate-600">Shipping momentum and delivery pace.</p>
                </div>
                <div className="rounded-2xl border border-slate-200/70 bg-slate-50 px-4 py-3 text-right">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">Overall</p>
                    <p className="mt-2 text-3xl font-semibold text-slate-900">{safeOverall}%</p>
                </div>
            </div>

            <div className="mt-4 space-y-4">
                {bars.map((bar) => (
                    <div key={bar.label}>
                        <div className="flex items-center justify-between text-sm">
                            <div>
                                <p className="font-medium text-slate-900">{bar.label}</p>
                                <p className="text-xs text-slate-500">{bar.helper}</p>
                            </div>
                            <span className="text-sm font-semibold text-slate-900">{bar.value}%</span>
                        </div>
                        <div className={`mt-2 h-2 w-full rounded-full ${bar.track}`}>
                            <div
                                className={`h-2 rounded-full ${bar.color} transition-all duration-700 ease-out`}
                                style={{ width: `${bar.value}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    );
}
