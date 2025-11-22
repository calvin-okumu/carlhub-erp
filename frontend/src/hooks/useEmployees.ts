import { User } from "@/api/types";
import { createUser, deleteUser, getUsers, updateUser } from "@/api/users";
import { useEffect, useState } from "react";
import { STORAGE_KEYS } from "@/constants/storage";

interface Employee extends User {
  role: string;
  tenant_name: string;
  is_approved: boolean;
}

export function useEmployees() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      // Note: This uses getUsers which fetches from /api/members/
      // We'll need to filter for employees or create a separate API call
      const users = await getUsers(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) || "");
      // Filter for employees - this is a temporary solution
      // Ideally we'd have a dedicated employee endpoint
      const employeeUsers = users.filter(
        () =>
          // This filtering logic needs to be implemented based on your data
          true, // Placeholder - adjust based on your UserTenant data
        );
      setEmployees(employeeUsers as Employee[]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch employees",
      );
    } finally {
      setLoading(false);
    }
  };

  const createEmployee = async (employeeData: Partial<Employee>) => {
    try {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      if (!token) throw new Error("No access token");

      // First create the user
      const newUser = await createUser(token, employeeData as CreateUserData);

      // Then add to tenant as employee (this would need a separate API call)
      // For now, just refetch
      await fetchEmployees();

      return newUser;
    } catch (err) {
      throw err;
    }
  };

  const updateEmployee = async (
    id: number,
    employeeData: Partial<Employee>,
  ) => {
    try {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      if (!token) throw new Error("No access token");

      await updateUser(token, id, employeeData);
      await fetchEmployees();
    } catch (err) {
      throw err;
    }
  };

  const deleteEmployee = async (id: number) => {
    try {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      if (!token) throw new Error("No access token");

      await deleteUser(token, id);
      await fetchEmployees();
    } catch (err) {
      throw err;
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  return {
    employees,
    loading,
    error,
    refetch: fetchEmployees,
    createEmployee,
    updateEmployee,
    deleteEmployee,
  };
}
