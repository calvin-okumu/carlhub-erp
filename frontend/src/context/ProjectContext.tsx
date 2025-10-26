"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { getProject } from '@/api/project_mgmt';
import type { Project } from '@/api/types';

interface ProjectContextType {
    project: Project | null;
    loading: boolean;
    error: string | null;
    refetch: () => void;
    activeTab: string;
    onTabChange: (tab: string) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export function ProjectProvider({ children, activeTab, onTabChange }: { children: React.ReactNode, activeTab: string, onTabChange: (tab: string) => void }) {
    const params = useParams();
    const id = params.slug as string;
    const [project, setProject] = useState<Project | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchProject = useCallback(async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setError('No access token');
            setLoading(false);
            return;
        }

        try {
            const data = await getProject(token, id);
            setProject(data);
        } catch (err) {
            console.error('Error loading project:', err);
            setError('Failed to load project');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchProject();
    }, [fetchProject]);

    return (
        <ProjectContext.Provider value={{ project, loading, error, refetch: fetchProject, activeTab, onTabChange }}>
            {children}
        </ProjectContext.Provider>
    );
}

export function useProject() {
    const context = useContext(ProjectContext);
    if (context === undefined) {
        throw new Error('useProject must be used within a ProjectProvider');
    }
    return context;
}