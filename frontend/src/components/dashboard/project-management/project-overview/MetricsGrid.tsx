import React from "react";
import { MetricCard } from "./MetricCard";
import { Target, CheckSquare, Zap, Users } from "lucide-react";

interface MetricsGridProps {
    milestonesCount: number;
    tasksCount: number;
    sprintsCount: number;
    teamMembersCount: number;
}

export default function MetricsGrid({
    milestonesCount,
    tasksCount,
    sprintsCount,
    teamMembersCount,
}: MetricsGridProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
                title="Milestones"
                value={milestonesCount}
                icon={Target}
                accentColor="blue"
            />
            <MetricCard
                title="Tasks"
                value={tasksCount}
                icon={CheckSquare}
                accentColor="green"
            />
            <MetricCard
                title="Sprints"
                value={sprintsCount}
                icon={Zap}
                accentColor="purple"
            />
            <MetricCard
                title="Team Members"
                value={teamMembersCount}
                icon={Users}
                accentColor="orange"
            />
        </div>
    );
}
