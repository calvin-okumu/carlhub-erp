 import ProjectSection from "@/components/dashboard/project-management/ProjectSection";

export default function ProjectManagementPage() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-6">
                <h1 className="h1-title">Projects Dashboard</h1>
                <p className="text-sm text-slate-600">
                    Monitor delivery health, timelines, and client progress in one place.
                </p>
            </div>
            <ProjectSection />
        </div>
    );
}
