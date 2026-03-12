"use client";
import React from "react";
import Card from "@/components/ui/Card";
import type { Project } from "@/api/types";

interface ProjectInformationProps {
    project: Project;
}

export default function ProjectInformation({ project }: ProjectInformationProps) {
    const formatDate = (date?: string) => {
        if (!date) return "—";
        return new Date(date).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    };

    const details = [
        { label: "Status", value: project.status || "—" },
        { label: "Client", value: project.client_name || "—" },
        {
            label: "Timeline",
            value: `${formatDate(project.start_date)} → ${formatDate(project.end_date)}`,
        },
        { label: "Budget", value: project.budget ? `$${project.budget.toLocaleString()}` : "Not set" },
        { label: "Priority", value: project.priority || "—" },
    ];

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-slate-900">Project Information</h2>
                <span className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Details</span>
            </div>

            <div className="divide-y divide-slate-100">
                {details.map(({ label, value }) => (
                    <div key={label} className="py-2.5 flex justify-between text-sm">
                        <span className="text-slate-500">{label}</span>
                        <span className="font-semibold text-slate-900 text-right">{value}</span>
                    </div>
                ))}
            </div>
        </Card>
    );
}
