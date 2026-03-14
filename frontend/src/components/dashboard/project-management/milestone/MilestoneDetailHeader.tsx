"use client";

import React from "react";
import { CalendarDays } from "lucide-react";
import type { Milestone } from "@/api/types";

interface MilestoneDetailHeaderProps {
  milestone: Milestone;
  projectSlug: string;
}

const statusStyles: Record<string, string> = {
  planning: "bg-amber-100 text-amber-700 border-amber-200",
  active: "bg-blue-100 text-blue-700 border-blue-200",
  completed: "bg-emerald-100 text-emerald-700 border-emerald-200",
};

const formatDate = (date?: string) => {
  if (!date) return "—";
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

export default function MilestoneDetailHeader({ milestone, projectSlug }: MilestoneDetailHeaderProps) {
  return (
    <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-semibold text-slate-900">{milestone.name}</h1>
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
                statusStyles[milestone.status] || statusStyles.planning
              }`}
            >
              {milestone.status}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-600">
            <span className="inline-flex items-center gap-2">
              <CalendarDays className="h-4 w-4" />
              Due {formatDate(milestone.due_date)}
            </span>
            <span className="inline-flex items-center gap-2">
              Progress <span className="font-semibold text-slate-900">{milestone.progress}%</span>
            </span>
          </div>
          {milestone.description ? (
            <p className="mt-3 text-sm text-slate-600 max-w-2xl">{milestone.description}</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
