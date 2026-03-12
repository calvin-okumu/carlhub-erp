import type { User, UserProfile } from "@/api/types";
import { createUser, deleteUser, getUsers, updateUser } from "@/api/users";
import { useEffect, useState } from "react";

interface Employee extends User {
  role: string;
  tenant_name: string;
  is_approved: boolean;
}

type EmployeeInput = Partial<UserProfile> & Partial<User>;
type CreateUserPayload = Parameters<typeof createUser>[1];

export function useEmployees() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      // Note: This uses getUsers which fetches from /api/members/
      // We'll need to filter for employees or create a separate API call
      const users = await getUsers(localStorage.getItem("access_token") || "");
      // Filter for employees - this is a temporary solution
      // Ideally we'd have a dedicated employee endpoint
      const employeeUsers = users.filter(
        (user) =>
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

  const createEmployee = async (employeeData: EmployeeInput) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No access token");

      if (!employeeData.first_name || !employeeData.last_name || !employeeData.email) {
        throw new Error("First name, last name, and email are required to create an employee");
      }

      const payload: CreateUserPayload = {
        first_name: employeeData.first_name,
        last_name: employeeData.last_name,
        email: employeeData.email,
        phone: employeeData.phone,
        job_title: employeeData.job_title,
        employee_id: employeeData.employee_id,
        employee_number: employeeData.employee_number,
        hire_date: employeeData.hire_date,
        street_address: employeeData.street_address,
        city: employeeData.city,
        state_province: employeeData.state_province,
        postal_code: employeeData.postal_code,
        country: employeeData.country,
        emergency_contact: employeeData.emergency_contact,
        emergency_phone: employeeData.emergency_phone,
        medical_aid_provider: employeeData.medical_aid_provider,
        medical_aid_plan: employeeData.medical_aid_plan,
        medical_aid_number: employeeData.medical_aid_number,
        medical_conditions: employeeData.medical_conditions,
        allergies: employeeData.allergies,
        medications: employeeData.medications,
        bank_name: employeeData.bank_name,
        account_number: employeeData.account_number,
        branch_code: employeeData.branch_code,
        account_type: employeeData.account_type,
        routing_number: employeeData.routing_number,
        swift_code: employeeData.swift_code,
        is_active: employeeData.is_active,
      };

      // First create the user
      const newUser = await createUser(token, payload);

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
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No access token");

      await updateUser(token, id, employeeData);
      await fetchEmployees();
    } catch (err) {
      throw err;
    }
  };

  const deleteEmployee = async (id: number) => {
    try {
      const token = localStorage.getItem("access_token");
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
