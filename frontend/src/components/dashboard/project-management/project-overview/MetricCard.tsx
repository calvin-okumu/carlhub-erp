
"use client";
import React from "react";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    accentColor?: string; // Tailwind color name (like "blue", "green", etc.)
    onClick?: () => void;
}

const accentStyles: Record<string, { text: string; bg: string; ring: string }> = {
    blue: {
        text: "text-sky-600",
        bg: "bg-sky-100",
        ring: "ring-sky-200",
    },
    green: {
        text: "text-emerald-600",
        bg: "bg-emerald-100",
        ring: "ring-emerald-200",
    },
    purple: {
        text: "text-violet-600",
        bg: "bg-violet-100",
        ring: "ring-violet-200",
    },
    orange: {
        text: "text-amber-600",
        bg: "bg-amber-100",
        ring: "ring-amber-200",
    },
};

export function MetricCard({
    title,
    value,
    icon: Icon,
    accentColor = "blue",
    onClick,
}: MetricCardProps) {
    const baseColor = accentStyles[accentColor] ?? accentStyles.blue;

    return (
        <div
            onClick={onClick}
            className={`group flex items-center justify-between gap-3 rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-slate-300 ${onClick ? "cursor-pointer" : ""
                }`}
        >
            <div className="flex items-center gap-4">
                <div
                    className={`relative flex items-center justify-center rounded-xl p-2.5 ring-1 ${baseColor.bg} ${baseColor.text} ${baseColor.ring}`}
                >
                    <Icon className="h-6 w-6" />
                </div>
                <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">{title}</p>
                    <p className="mt-1 text-3xl font-semibold text-slate-900 leading-tight">
                        {value}
                    </p>
                </div>
            </div>
        </div>
    );
}
