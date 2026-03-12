 import ProjectSection from "@/components/dashboard/project-management/ProjectSection";

export default function ProjectManagementPage() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
            <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-6 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">Project portfolio</p>
                <h1 className="mt-2 text-2xl font-semibold text-slate-900">Projects Dashboard</h1>
                <p className="mt-2 text-sm text-slate-600">
                    Monitor delivery health, timelines, and client progress in one place.
                </p>
            </div>
            <ProjectSection />
        </div>
    );
}
