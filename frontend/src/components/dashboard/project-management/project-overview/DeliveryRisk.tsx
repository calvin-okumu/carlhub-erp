import React from "react";
import Card from "@/components/ui/Card";
import type { Project } from "@/api/types";

interface DeliveryRiskProps {
    project: Project;
    timelineProgress: number | null;
    milestonesCount: number;
    tasksCount: number;
    sprintsCount: number;
}

const clampValue = (value: number) => Math.min(Math.max(Math.round(value), 0), 100);

export default function DeliveryRisk({
    project,
    timelineProgress,
    milestonesCount,
    tasksCount,
    sprintsCount,
}: DeliveryRiskProps) {
    const deliveryProgress = clampValue(project.progress ?? 0);
    const scheduleProgress = timelineProgress === null ? 0 : clampValue(timelineProgress);
    const gap = scheduleProgress - deliveryProgress;

    const riskLevel = (() => {
        if (deliveryProgress < 40 || gap > 20) return "High";
        if (deliveryProgress < 60 || gap > 10) return "Medium";
        return "Low";
    })();

    const riskTone = {
        Low: "bg-emerald-50 border-emerald-200 text-emerald-700",
        Medium: "bg-amber-50 border-amber-200 text-amber-700",
        High: "bg-rose-50 border-rose-200 text-rose-700",
    };

    const deliveryConfidence = clampValue(
        deliveryProgress + (milestonesCount > 0 ? 8 : -8) - (gap > 0 ? gap / 2 : 0)
    );
    const scheduleAlignment = clampValue(timelineProgress === null ? 55 : 100 - Math.max(0, gap));
    const resourcingHealth = clampValue(50 + Math.min(40, project.team_members.length * 5));

    const indicators = [
        { label: "Delivery confidence", value: deliveryConfidence, color: "bg-emerald-500" },
        { label: "Schedule alignment", value: scheduleAlignment, color: "bg-cyan-500" },
        { label: "Resourcing", value: resourcingHealth, color: "bg-amber-500" },
    ];

    const insights = [
        timelineProgress === null
            ? "Timeline dates missing"
            : gap > 0
              ? `Schedule ahead by ${Math.round(gap)}%`
              : `Delivery ahead by ${Math.abs(Math.round(gap))}%`,
        milestonesCount === 0
            ? "Milestones not mapped"
            : `${milestonesCount} milestones mapped`,
        `${tasksCount} tasks across ${sprintsCount} sprints`,
    ];

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !bg-white/90 !shadow-sm p-4 text-slate-900">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-semibold text-slate-900">Delivery Risk</h2>
                    <p className="text-xs text-slate-600">Confidence and risk drivers</p>
                </div>
                <div className={`rounded-full border px-3 py-1 text-sm font-semibold ${riskTone[riskLevel]}`}>
                    {riskLevel}
                </div>
            </div>

            <div className="space-y-4">
                {indicators.map((indicator) => (
                    <div key={indicator.label}>
                        <div className="flex items-center justify-between text-sm text-slate-600">
                            <span>{indicator.label}</span>
                            <span className="font-semibold text-slate-900">{indicator.value}%</span>
                        </div>
                        <div className="mt-2 h-2 w-full rounded-full bg-slate-200">
                            <div
                                className={`h-2 rounded-full ${indicator.color} transition-all duration-700`}
                                style={{ width: `${indicator.value}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-4 space-y-2 rounded-xl border border-slate-200/70 bg-slate-50 p-3 text-xs text-slate-600">
                {insights.map((insight) => (
                    <p key={insight}>{insight}</p>
                ))}
            </div>
        </Card>
    );
}
