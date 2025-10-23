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
        <Card className="p-5">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Project Timeline</h2>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={onViewAll}
                    className="text-sm"
                >
                    View All
                </Button>
            </div>

            {/* Content */}
            {hasMilestones ? (
                <div className="space-y-3">
                    {/* Placeholder timeline — replace with actual milestone list */}
                    <p className="text-gray-700">Milestones timeline coming soon…</p>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center text-center py-10 text-gray-500 border border-dashed border-gray-200 rounded-lg">
                    <p className="text-sm">No milestones yet</p>
                    <p className="text-xs text-gray-400 mt-1">
                        Create a milestone to start tracking progress
                    </p>
                </div>
            )}
        </Card>
    );
}
