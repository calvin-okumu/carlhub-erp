import React from "react";
import Card from "@/components/ui/Card";

import type { Project } from "@/api/types";
import { AlertTriangle, CheckCircle2, Activity } from "lucide-react";

interface ProjectHealthProps {
    project: Project;
    overdueTasks?: number;
}

export default function ProjectHealth({ project, overdueTasks = 0 }: ProjectHealthProps) {
    // --- Smart derived health logic ---
    const getHealthStatus = () => {
        if (overdueTasks > 5 || project.progress < 30) return "Critical";
        if (overdueTasks > 0 || project.progress < 70) return "At Risk";
        return "On Track";
    };

    const healthStatus = getHealthStatus();

    const getHealthScore = () => {
        let score = project.progress ?? 0;
        if (overdueTasks > 0) score -= overdueTasks * 5;
        if (project.milestones_count > 0) score += 10;
        return Math.max(0, Math.min(100, score));
    };

    const healthScore = getHealthScore();

    const getHealthIcon = () => {
        switch (healthStatus) {
            case "On Track":
                return <CheckCircle2 className="text-green-500" />;
            case "At Risk":
                return <Activity className="text-yellow-500" />;
            case "Critical":
                return <AlertTriangle className="text-red-500" />;
            default:
                return null;
        }
    };

    const getHealthColor = () => {
        switch (healthStatus) {
            case "On Track":
                return "bg-emerald-50 border-emerald-200 text-emerald-700";
            case "At Risk":
                return "bg-amber-50 border-amber-200 text-amber-700";
            case "Critical":
                return "bg-rose-50 border-rose-200 text-rose-700";
            default:
                return "";
        }
    };

    const getProgressColor = () => {
        if (healthScore >= 70) return "bg-emerald-400";
        if (healthScore >= 40) return "bg-amber-400";
        return "bg-rose-400";
    };

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !bg-white/90 !shadow-sm p-4 space-y-3 text-slate-900">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-semibold text-slate-900">Project Health</h2>
                    <p className="text-xs text-slate-600">Delivery risk overview</p>
                </div>
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-semibold ${getHealthColor()}`}>
                    {getHealthIcon()}
                    <span>{healthStatus}</span>
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <div className="flex justify-between text-sm mb-2 text-slate-600">
                        <span>Health Score</span>
                        <span className="font-semibold text-slate-900">{healthScore}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full transition-all duration-500 ${getProgressColor()}`}
                            style={{ width: `${healthScore}%` }}
                        ></div>
                    </div>
                </div>

                <div className="space-y-3 text-sm text-slate-600">
                    <div className="flex justify-between">
                        <span>Milestones Completed</span>
                        <span className="font-semibold text-slate-900">{project.milestones_count ?? 0}</span>
                    </div>
                    <div className="flex justify-between">
                        <span>Tasks Overdue</span>
                        <span className={overdueTasks > 0 ? "text-rose-600 font-semibold" : "text-slate-900 font-semibold"}>
                            {overdueTasks}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span>Progress</span>
                        <span className="font-semibold text-slate-900">{project.progress ?? 0}%</span>
                    </div>
                </div>
            </div>
        </Card>
    );
}
