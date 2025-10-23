"use client";

import React from 'react';
import { LucideIcon } from 'lucide-react';
import StatCard from '@/components/ui/StatCard';

interface Metric {
    title: string;
    value: number;
    label: string;
    icon: LucideIcon;
    color: string;
}

interface MetricsBarProps {
    metrics: Metric[];
}

export default function MetricsBar({ metrics }: MetricsBarProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {metrics.map((metric, index) => (
                <StatCard
                    key={index}
                    title={metric.title}
                    value={metric.value}
                    icon={metric.icon}
                    color={metric.color}
                />
            ))}
        </div>
    );
}