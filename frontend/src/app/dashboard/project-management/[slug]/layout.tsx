"use client";

import { ProjectProvider } from '@/context/ProjectContext';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <ProjectProvider activeTab="" onTabChange={() => {}}>
      {children}
    </ProjectProvider>
  );
}
