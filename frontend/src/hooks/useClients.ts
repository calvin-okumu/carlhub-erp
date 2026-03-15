import { useCallback, useEffect, useState } from "react";
import {
    Client,
    CreateClientData,
    UpdateClientData,
    createClient,
    deleteClient,
    getClients,
    getUserTenants,
    updateClient,
    UserTenant,
    PaginatedResponse,
} from "../api";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function useClients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [currentTenant, setCurrentTenant] = useState<UserTenant | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<{ count: number; next: string | null; previous: string | null } | null>(null);

  const fetchClients = useCallback(async (params?: { page?: number; limit?: number; search?: string; ordering?: string; status?: string }) => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const tenants = await getUserTenants(token);
      const ownerTenant = Array.isArray(tenants) ? tenants.find((t) => t.is_owner) || tenants[0] : tenants;
      setCurrentTenant(ownerTenant || null);

      if (!ownerTenant) {
        setClients([]);
        setPagination(null);
        return;
      }

      const data = await getClients(token, { tenant: ownerTenant.tenant, ordering: '-created_at', ...params });
      if (params?.page || params?.limit) {
        // Paginated response
        const paginatedData = data as PaginatedResponse<Client>;
        setClients(paginatedData.results);
        setPagination({
          count: paginatedData.count,
          next: paginatedData.next,
          previous: paginatedData.previous,
        });
      } else {
        // Non-paginated response
        setClients(data as Client[]);
        setPagination(null);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to load data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Remove initial fetch - let components handle their own data loading
  // useEffect(() => {
  //   fetchClients();
  // }, [fetchClients]);

  const addClient = async (data: CreateClientData) => {
    const token = getToken();
    if (!token || !currentTenant) return;

    // Temporary client for optimistic update
    const tempClient: Client = {
      id: Date.now().toString(), // temporary id
      slug: '', // will be set by backend
      name: data.name,
      email: data.email,
      phone: data.phone || '',
      status: data.status,
      tenant: currentTenant.tenant,
      tenant_name: currentTenant.tenant_name,
      projects_count: '0',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setClients(prev => [...prev, tempClient]);

    setLoading(true);
    try {
      const newClient = await createClient(token, { ...data, tenant: currentTenant.tenant });
      setClients(prev => prev.map(c => c.id === tempClient.id ? newClient : c));
    } catch (err) {
      setClients(prev => prev.filter(c => c.id !== tempClient.id));
      setError(err instanceof Error ? err.message : "Failed to create client.");
    } finally {
      setLoading(false);
    }
  };

  const editClient = async (slug: string, data: UpdateClientData) => {
    const token = getToken();
    if (!token) return;

    const originalClient = clients.find(c => c.slug === slug);
    if (!originalClient) return;

    // Optimistic update — cast tenant to string to satisfy Client type
    setClients(prev => prev.map(c =>
      c.slug === slug
        ? { ...c, ...data, tenant: data.tenant !== undefined ? String(data.tenant) : c.tenant }
        : c
    ));

    setLoading(true);
    try {
      const updatedClient = await updateClient(token, slug, data);
      setClients(prev => prev.map(c => c.slug === slug ? updatedClient : c));
    } catch (err) {
      // Revert on error
      setClients(prev => prev.map(c => c.slug === slug ? originalClient : c));
      setError(err instanceof Error ? err.message : "Failed to update client.");
    } finally {
      setLoading(false);
    }
  };

  const removeClient = async (slug: string) => {
    const token = getToken();
    if (!token) return;

    const clientToRemove = clients.find(c => c.slug === slug);
    if (!clientToRemove) return;

    setClients((prev) => prev.filter((c) => c.slug !== slug));

    setLoading(true);
    try {
      await deleteClient(token, slug);
    } catch (err) {
      setClients((prev) => [...prev, clientToRemove]);
      setError(err instanceof Error ? err.message : "Failed to delete client.");
    } finally {
      setLoading(false);
    }
  };

  return {
    clients,
    currentTenant,
    loading,
    error,
    pagination,
    addClient,
    editClient,
    removeClient,
    refetch: fetchClients,
    setError,
  };
}
