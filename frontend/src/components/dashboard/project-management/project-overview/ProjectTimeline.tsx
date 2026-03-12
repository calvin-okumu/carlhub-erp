"use client";
import React from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

interface ProjectTimelineProps {
    milestonesCount: number;
    onViewAll?: () => void;
}

export default function ProjectTimeline({
    milestonesCount,
    onViewAll,
}: ProjectTimelineProps) {
    const hasMilestones = milestonesCount > 0;

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-semibold text-slate-900">Project Timeline</h2>
                    <p className="text-xs text-slate-500">Milestones and key delivery checkpoints.</p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={onViewAll}
                    className="text-sm"
                >
                    View All
                </Button>
            </div>

            {hasMilestones ? (
                <div className="space-y-3">
                    <p className="text-slate-700">Milestones timeline coming soon…</p>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center text-center py-10 text-slate-500 border border-dashed border-slate-200 rounded-xl bg-slate-50/70">
                    <p className="text-sm">No milestones yet</p>
                    <p className="text-xs text-slate-400 mt-1">
                        Create a milestone to start tracking progress
                    </p>
                </div>
            )}
        </Card>
    );
}
