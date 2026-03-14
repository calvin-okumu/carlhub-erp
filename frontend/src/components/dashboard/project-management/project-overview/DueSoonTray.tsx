import React from "react";
import Card from "@/components/ui/Card";
import { Clock, AlertTriangle } from "lucide-react";
import type { Milestone } from "@/api/types";

interface DueSoonTrayProps {
    milestones: Milestone[];
    windowDays?: number;
}

const MS_PER_DAY = 1000 * 60 * 60 * 24;

const formatDate = (date?: string) => {
    if (!date) return "—";
    return new Date(date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
    });
};

export default function DueSoonTray({ milestones, windowDays = 14 }: DueSoonTrayProps) {
    const now = Date.now();
    const dueSoon = milestones
        .filter((milestone) => milestone.due_date)
        .map((milestone) => {
            const dueDate = new Date(milestone.due_date as string).getTime();
            const daysUntil = Math.ceil((dueDate - now) / MS_PER_DAY);
            return {
                ...milestone,
                dueDate,
                daysUntil,
            };
        })
        .filter((milestone) => milestone.daysUntil <= windowDays)
        .sort((a, b) => a.dueDate - b.dueDate)
        .slice(0, 4);

    return (
        <Card className="!rounded-2xl !border-slate-200/70 !bg-white/90 !shadow-sm p-4 text-slate-900">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-semibold text-slate-900">Due Soon</h2>
                    <p className="text-xs text-slate-600">Next {windowDays} days</p>
                </div>
                <span className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">Milestones</span>
            </div>

            {dueSoon.length === 0 ? (
                <div className="flex flex-col items-center justify-center text-center py-6 text-slate-500 border border-dashed border-slate-200 rounded-xl bg-slate-50">
                    <p className="text-sm text-slate-600">No upcoming milestone deadlines</p>
                    <p className="text-xs text-slate-500 mt-1">You are clear for now</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {dueSoon.map((milestone) => {
                        const isOverdue = milestone.daysUntil < 0;
                        const dueLabel = isOverdue
                            ? `${Math.abs(milestone.daysUntil)}d overdue`
                            : milestone.daysUntil === 0
                                ? "Due today"
                                : `Due in ${milestone.daysUntil}d`;

                        return (
                            <div
                                key={milestone.id}
                                className="flex items-center justify-between rounded-xl border border-slate-200/70 bg-white px-3 py-2"
                            >
                                <div>
                                    <p className="text-sm font-semibold text-slate-900">{milestone.name}</p>
                                    <p className="text-xs text-slate-600">{formatDate(milestone.due_date)}</p>
                                </div>
                                <div className={`flex items-center gap-2 text-xs font-semibold ${isOverdue ? "text-rose-600" : "text-slate-600"}`}>
                                    {isOverdue ? <AlertTriangle className="h-4 w-4" /> : <Clock className="h-4 w-4" />}
                                    <span>{dueLabel}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </Card>
    );
}
