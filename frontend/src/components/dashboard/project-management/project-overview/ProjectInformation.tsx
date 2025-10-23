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
        <Card className="p-5">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h2>

            <div className="divide-y divide-gray-100">
                {details.map(({ label, value }) => (
                    <div key={label} className="py-2 flex justify-between text-sm">
                        <span className="text-gray-600">{label}</span>
                        <span className="font-medium text-gray-900 text-right">{value}</span>
                    </div>
                ))}
            </div>
        </Card>
    );
}
