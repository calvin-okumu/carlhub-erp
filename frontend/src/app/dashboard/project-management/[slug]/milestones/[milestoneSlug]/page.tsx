"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import type { Milestone } from "@/api/types";
import { getMilestones } from "@/api/project_mgmt";
import Loader from "@/components/shared/Loader";
import { useProject } from "@/context/ProjectContext";
import ProjectLayout from "@/components/dashboard/project-management/ProjectLayout";
import MilestoneDetailHeader from "@/components/dashboard/project-management/milestone/MilestoneDetailHeader";
import SprintSection from "@/components/dashboard/project-management/sprint/SprintSection";

export default function MilestoneDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { project, loading: projectLoading, error: projectError } = useProject();
  const [milestone, setMilestone] = useState<Milestone | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const projectSlug = params?.slug as string | undefined;
  const milestoneSlug = params?.milestoneSlug as string | undefined;

  useEffect(() => {
    const fetchMilestone = async () => {
      const token = localStorage.getItem("access_token");
      if (!token || !projectSlug || !milestoneSlug) {
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const data = await getMilestones(token, { projectSlug });
        const match = data.results.find((item) => item.slug === milestoneSlug);
        if (!match) {
          setError("Milestone not found.");
        } else {
          setMilestone(match);
        }
      } catch (err) {
        console.error(err);
        setError("Failed to load milestone details.");
      } finally {
        setLoading(false);
      }
    };

    fetchMilestone();
  }, [projectSlug, milestoneSlug]);

  const handleTabChange = (tab: string) => {
    if (!project?.slug) return;
    router.push(`/dashboard/project-management/${project.slug}?tab=${tab}`);
  };

  if (projectLoading) return <Loader />;
  if (projectError) return <div className="text-red-500">{projectError}</div>;
  if (!project) return <div>Project not found</div>;

  if (loading) return <Loader />;
  if (error || !milestone) return <div className="text-red-500">{error || "Milestone not found"}</div>;

  return (
    <ProjectLayout project={project} activeTab="milestones" onTabChange={handleTabChange}>
      <div className="space-y-6">
        <MilestoneDetailHeader milestone={milestone} projectSlug={project.slug} />
        <SprintSection milestoneSlug={milestone.slug} embedded />
      </div>
    </ProjectLayout>
  );
}
