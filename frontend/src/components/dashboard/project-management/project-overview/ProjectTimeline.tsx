"use client";
import React from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

interface ProjectTimelineProps {
    milestonesCount: number;
    timelineProgress: number | null;
    startDate?: string;
    endDate?: string;
    onViewAll?: () => void;
}

export default function ProjectTimeline({
    milestonesCount,
    timelineProgress,
    startDate,
    endDate,
    onViewAll,
}: ProjectTimelineProps) {
    const hasMilestones = milestonesCount > 0;
    const safeTimeline = timelineProgress === null ? 0 : Math.min(Math.max(Math.round(timelineProgress), 0), 100);
    const formatDate = (date?: string) => {
        if (!date) return "—";
        return new Date(date).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
        });
    };

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !bg-white/90 !shadow-sm p-4 text-slate-900">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-semibold text-slate-900">Project Timeline</h2>
                    <p className="text-xs text-slate-600">Milestones and key delivery checkpoints.</p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={onViewAll}
                    className="text-sm border-slate-200 text-slate-700 hover:border-slate-300 hover:text-slate-900"
                >
                    View All
                </Button>
            </div>

            <div className="rounded-xl border border-slate-200/70 bg-slate-50 p-3">
                <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{formatDate(startDate)}</span>
                    <span>{formatDate(endDate)}</span>
                </div>
                <div className="mt-3 h-2 w-full rounded-full bg-slate-200">
                    <div
                        className="h-2 rounded-full bg-cyan-500 transition-all duration-700"
                        style={{ width: `${safeTimeline}%` }}
                    />
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                    <span>{timelineProgress === null ? "Timeline not set" : "Schedule elapsed"}</span>
                    <span>{timelineProgress === null ? "—" : `${safeTimeline}%`}</span>
                </div>
            </div>

            {hasMilestones ? (
                <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="rounded-xl border border-slate-200/70 bg-white p-3">
                        <p className="text-xs text-slate-500">Milestones mapped</p>
                        <p className="mt-2 text-lg font-semibold text-slate-900">{milestonesCount}</p>
                    </div>
                    <div className="rounded-xl border border-slate-200/70 bg-white p-3">
                        <p className="text-xs text-slate-500">Next checkpoint</p>
                        <p className="mt-2 text-sm font-semibold text-slate-900">Upcoming milestone</p>
                    </div>
                </div>
            ) : (
                <div className="mt-4 flex flex-col items-center justify-center text-center py-6 text-slate-500 border border-dashed border-slate-200 rounded-xl bg-slate-50">
                    <p className="text-sm text-slate-600">No milestones yet</p>
                    <p className="text-xs text-slate-500 mt-1">
                        Create a milestone to start tracking progress
                    </p>
                </div>
            )}
        </Card>
    );
}
