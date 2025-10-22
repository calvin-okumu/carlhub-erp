
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
            className={`group flex items-center p-6 rounded-2xl bg-white border border-gray-100 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 ${onClick ? "cursor-pointer" : ""
                }`}
        >
            {/* Icon Section */}
            <div
                className={`relative flex items-center justify-center p-3.5 mr-4 rounded-xl ${baseColor.bg} ${baseColor.text} ring-4 ${baseColor.ring}`}
            >
                <Icon className="h-7 w-7" />
            </div>

            {/* Content Section */}
            <div className="flex items-center">
                <span className="text-3xl font-semibold text-gray-900 leading-tight mr-2">
                    {value}
                </span>
                <span className="text-sm text-gray-500 font-medium tracking-wide">
                    {title}
                </span>
            </div>
        </div>
    );
}
