
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

export function MetricCard({
    title,
    value,
    icon: Icon,
    accentColor = "blue",
    onClick,
}: MetricCardProps) {
    const baseColor = {
        text: `text-${accentColor}-600`,
        bg: `bg-${accentColor}-50`,
        ring: `ring-${accentColor}-100`,
    };

    return (
        <div
            onClick={onClick}
            className={`group flex items-center justify-between gap-4 p-5 rounded-2xl bg-white/90 border border-slate-200/70 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-md ${onClick ? "cursor-pointer" : ""
                }`}
        >
            <div className="flex items-center gap-4">
                <div
                    className={`relative flex items-center justify-center p-3 rounded-xl ${baseColor.bg} ${baseColor.text} ring-4 ${baseColor.ring}`}
                >
                    <Icon className="h-6 w-6" />
                </div>
                <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">{title}</p>
                    <p className="mt-2 text-3xl font-semibold text-slate-900 leading-tight">
                        {value}
                    </p>
                </div>
            </div>
        </div>
    );
}
