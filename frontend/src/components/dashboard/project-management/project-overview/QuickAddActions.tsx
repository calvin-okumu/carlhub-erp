import React from "react";
import { PlusCircle, Flag, Zap } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function QuickAddActions() {
    return (
        <Card className="!rounded-2xl !border-slate-200/70 !shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-lg font-semibold text-slate-900">Quick Add</h2>
                    <p className="text-xs text-slate-500">Create faster</p>
                </div>
                <span className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-400">Actions</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <Button variant="outline" className="w-full gap-2 rounded-full border-slate-200/70 text-slate-700">
                    <PlusCircle className="h-4 w-4" />
                    Task
                </Button>
                <Button variant="outline" className="w-full gap-2 rounded-full border-slate-200/70 text-slate-700">
                    <Flag className="h-4 w-4" />
                    Milestone
                </Button>
                <Button variant="outline" className="w-full gap-2 rounded-full border-slate-200/70 text-slate-700">
                    <Zap className="h-4 w-4" />
                    Sprint
                </Button>
            </div>

            <p className="text-xs text-slate-500 mt-4">
                Add items directly to this project without leaving the overview.
            </p>
        </Card>
    );
}
