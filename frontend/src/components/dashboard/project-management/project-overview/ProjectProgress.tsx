
import React from "react";
import Card from "@/components/ui/Card";

interface ProjectProgressProps {
    progress: number; // 0–100
}

export default function ProjectProgress({ progress }: ProjectProgressProps) {
    const safeProgress = Math.min(Math.max(progress, 0), 100);

    const getProgressColor = () => {
        if (safeProgress < 40) return "bg-red-500";
        if (safeProgress < 75) return "bg-yellow-500";
        return "bg-green-500";
    };

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-900">Project Progress</h2>
                <span className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Overview</span>
            </div>

            <div>
                <p className="text-sm text-slate-500 mb-2">Overall completion</p>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                    <div
                        className={`h-3 rounded-full ${getProgressColor()} transition-all duration-700 ease-out`}
                        style={{ width: `${safeProgress}%` }}
                    />
                </div>
                <div className="flex justify-between items-center mt-2 text-sm text-slate-600">
                    <span>Progress</span>
                    <span className="font-semibold text-slate-900">{safeProgress}%</span>
                </div>
            </div>
        </Card>
    );
}
