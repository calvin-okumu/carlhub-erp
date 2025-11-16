"use client";
import { PolicyHeader } from "./PolicyHeader";
import { PolicyRules } from "./PolicyRules";

export const PolicySection = () => {
    return (
        <div className="space-y-4">
            <PolicyHeader />
            <PolicyRules />
        </div>
    )
}

