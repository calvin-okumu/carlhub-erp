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
} from "../api";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function useClients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [currentTenant, setCurrentTenant] = useState<UserTenant | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchClients = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    try {
      const tenants = await getUserTenants(token);
      const ownerTenant = Array.isArray(tenants) ? tenants.find((t) => t.is_owner) || tenants[0] : tenants;
      setCurrentTenant(ownerTenant || null);

      const data = await getClients(token, { ordering: '-created_at' });
      setClients(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  const addClient = async (data: CreateClientData) => {
    const token = getToken();
    if (!token || !currentTenant) return;

    // Temporary client for optimistic update
    const tempClient: Client = {
      id: Date.now(), // temporary id
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

  const editClient = async (id: number, data: UpdateClientData) => {
    const token = getToken();
    if (!token) return;

    const originalClient = clients.find(c => c.id === id);
    if (!originalClient) return;

    // Optimistic update
    setClients(prev => prev.map(c => c.id === id ? { ...c, ...data } : c));

    setLoading(true);
    try {
      const updatedClient = await updateClient(token, id, data);
      setClients(prev => prev.map(c => c.id === id ? updatedClient : c));
    } catch (err) {
      // Revert on error
      setClients(prev => prev.map(c => c.id === id ? originalClient : c));
      setError(err instanceof Error ? err.message : "Failed to update client.");
    } finally {
      setLoading(false);
    }
  };

  const removeClient = async (id: number) => {
    const token = getToken();
    if (!token) return;

    const clientToRemove = clients.find(c => c.id === id);
    if (!clientToRemove) return;

    setClients((prev) => prev.filter((c) => c.id !== id));

    setLoading(true);
    try {
      await deleteClient(token, id);
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
    addClient,
    editClient,
    removeClient,
    refetch: fetchClients,
    setError,
  };
}
