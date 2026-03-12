 "use client";

 interface ProjectTabsProps {
     activeTab: string;
     onTabChange: (tab: string) => void;
 }

 const tabs = [
     { id: "overview", label: "Overview" },
     { id: "milestones", label: "Milestones" },
     { id: "backlog", label: "Backlog" },
     { id: "sprints", label: "Sprints" },
     { id: "documents", label: "Documents" },
     { id: "completed-tasks", label: "Completed Tasks" },
 ];

 export default function ProjectTabs({ activeTab, onTabChange }: ProjectTabsProps) {
    return (
        <div className="bg-white/90 rounded-2xl shadow-sm border border-slate-200/70">
            <nav
                className="flex flex-wrap relative gap-x-1"
                aria-label="Project sections"
            >
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.id;

                    const className = `
                        relative py-3 px-5 text-sm font-semibold transition-colors duration-200
                        focus:outline-none
                        ${isActive
                            ? "text-slate-900"
                            : "text-slate-500 hover:text-slate-800"}
                    `;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange(tab.id)}
                            className={className}
                        >
                            {tab.label}
                            {isActive && (
                                <div className="absolute left-4 right-4 -bottom-[1px] h-[2px] bg-slate-900 rounded-full" />
                            )}
                        </button>
                    );
                })}
            </nav>
        </div>
    );
}
