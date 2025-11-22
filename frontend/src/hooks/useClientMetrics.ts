"use client";

import { useState, useEffect, useCallback } from 'react';
import { getClients } from '@/api/crm';
import type { Client } from '@/api/types';

interface ClientMetrics {
    totalClients: number;
    activeClients: number;
    prospects: number;
    newClientsThisMonth: number;
}

interface UseClientMetricsReturn {
    metrics: ClientMetrics;
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
}

export function useClientMetrics(): UseClientMetricsReturn {
    const [metrics, setMetrics] = useState<ClientMetrics>({
        totalClients: 0,
        activeClients: 0,
        prospects: 0,
        newClientsThisMonth: 0,
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const calculateMetrics = useCallback((clients: Client[]): ClientMetrics => {
        const totalClients = clients.length;
        const activeClients = clients.filter(c => c.status === 'active').length;
        const prospects = clients.filter(c => c.status === 'prospect').length;
        const newClientsThisMonth = clients.filter(c => {
            const created = new Date(c.created_at);
            const now = new Date();
            return created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear();
        }).length;

        return {
            totalClients,
            activeClients,
            prospects,
            newClientsThisMonth,
        };
    }, []);

    const fetchMetrics = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            const data = await getClients({ limit: 1000 });
            
            let clients: Client[] = [];
            if (data && typeof data === 'object' && 'results' in data) {
                clients = data.results;
            } else {
                clients = data as Client[];
            }
            
            const calculatedMetrics = calculateMetrics(clients);
            setMetrics(calculatedMetrics);
        } catch (err) {
            console.error('Failed to fetch client metrics:', err);
            setError(err instanceof Error ? err.message : 'Failed to load client metrics');
            setMetrics({
                totalClients: 0,
                activeClients: 0,
                prospects: 0,
                newClientsThisMonth: 0,
            });
        } finally {
            setLoading(false);
        }
    }, [calculateMetrics]);

    useEffect(() => {
        fetchMetrics();
    }, [fetchMetrics]);

    return {
        metrics,
        loading,
        error,
        refetch: fetchMetrics,
    };
}