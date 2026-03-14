"use client";

import { useParams, useRouter } from "next/navigation";
import KanbanSection from "@/components/dashboard/project-management/sprint/kanban/KanbanSection";

export default function SprintKanbanPage() {
  const params = useParams();
  const router = useRouter();
  const sprintSlug = params?.sprintSlug as string | undefined;
  const projectSlug = params?.slug as string | undefined;

  if (!sprintSlug) {
    return <div className="p-6 text-slate-600">Sprint not found</div>;
  }

  return (
    <KanbanSection
      sprintSlug={sprintSlug}
      onBack={() => {
        if (projectSlug) {
          router.push(`/dashboard/project-management/${projectSlug}?tab=sprints`);
        } else {
          router.push(`/dashboard/project-management`);
        }
      }}
    />
  );
}
