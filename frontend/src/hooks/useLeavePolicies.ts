import { useState, useEffect, useCallback } from "react";
import {
  getLeavePolicies,
  createLeavePolicy,
  updateLeavePolicy,
  patchLeavePolicy,
  deleteLeavePolicy,
  type LeavePolicy,
  type PaginatedResponse,
} from "../api";
export const useLeavePolicies = (params?: {
  leave_type?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}) => {
  const [policies, setPolicies] = useState<LeavePolicy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<{
    count: number;
    next: string | null;
    previous: string | null;
  } | null>(null);
  const fetchPolicies = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response: PaginatedResponse<LeavePolicy> | LeavePolicy[] = await getLeavePolicies(params);

      let policiesData: LeavePolicy[] = [];
      let paginationData: { count: number; next: string | null; previous: string | null } | null = null;

      if (response && typeof response === 'object' && 'results' in response) {
        // Paginated response
        policiesData = response.results || [];
        paginationData = {
          count: response.count,
          next: response.next,
          previous: response.previous,
        };
      } else if (Array.isArray(response)) {
        // Direct array response
        policiesData = response;
        paginationData = {
          count: response.length,
          next: null,
          previous: null,
        };
      }

      setPolicies(policiesData);
      if (paginationData) {
        setPagination(paginationData);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch leave policies",
      );
      console.error("Error fetching leave policies:", err);
    } finally {
      setIsLoading(false);
    }
  }, [params]);
  useEffect(() => {
    fetchPolicies();
  }, [fetchPolicies]);
  const createPolicy = async (
    data: Omit<
      LeavePolicy,
      "id" | "slug" | "tenant" | "tenant_name" | "created_at" | "updated_at"
    >,
  ) => {
    try {
      const newPolicy = await createLeavePolicy(data);
      setPolicies((prev) => [newPolicy, ...prev]);
      return newPolicy;
    } catch (err) {
      throw err;
    }
  };
  const updatePolicy = async (slug: string, data: Partial<LeavePolicy>) => {
    try {
      const updatedPolicy = await updateLeavePolicy(slug, data);
      setPolicies((prev) =>
        prev.map((policy) => (policy.slug === slug ? updatedPolicy : policy)),
      );
      return updatedPolicy;
    } catch (err) {
      throw err;
    }
  };
  const patchPolicy = async (slug: string, data: Partial<LeavePolicy>) => {
    try {
      const updatedPolicy = await patchLeavePolicy(slug, data);
      setPolicies((prev) =>
        prev.map((policy) => (policy.slug === slug ? updatedPolicy : policy)),
      );
      return updatedPolicy;
    } catch (err) {
      throw err;
    }
  };
  const deletePolicy = async (slug: string) => {
    try {
      await deleteLeavePolicy(slug);
      setPolicies((prev) => prev.filter((policy) => policy.slug !== slug));
    } catch (err) {
      throw err;
    }
  };
  const refetch = () => {
    fetchPolicies();
  };
  return {
    policies,
    isLoading,
    error,
    pagination,
    createPolicy,
    updatePolicy,
    patchPolicy,
    deletePolicy,
    refetch,
  };
};
