
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
        <Card className="p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">Project Progress</h2>

            <div>
                <p className="text-sm text-gray-500 mb-2">Overall Completion</p>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                        className={`h-3 rounded-full ${getProgressColor()} transition-all duration-700 ease-out`}
                        style={{ width: `${safeProgress}%` }}
                    />
                </div>
                <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">Progress</span>
                    <span className="text-sm font-medium text-gray-900">{safeProgress}%</span>
                </div>
            </div>
        </Card>
    );
}
