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
         <div className="bg-white rounded-xl shadow-sm mb-6 border border-gray-100">
             <nav
                 className="flex flex-wrap relative"
                 aria-label="Project sections"
             >
                 {tabs.map((tab) => {
                     const isActive = activeTab === tab.id;

                     const className = `
                         relative py-3 px-5 text-sm font-medium transition-colors duration-200
                         focus:outline-none
                         ${isActive
                             ? "text-blue-600"
                             : "text-gray-500 hover:text-gray-800"}
                     `;

                     return (
                         <button
                             key={tab.id}
                             onClick={() => onTabChange(tab.id)}
                             className={className}
                         >
                             {tab.label}
                             {isActive && (
                                 <div className="absolute left-0 right-0 -bottom-[1px] h-[2px] bg-blue-600 rounded-full" />
                             )}
                         </button>
                     );
                 })}
             </nav>
         </div>
     );
 }
