import { useEffect, useState } from "react";
import { STORAGE_KEYS } from "../constants/storage";
interface UserRole {
  role: string;
  canApproveLeave: boolean;
  canApproveAtLevel: (level: string) => boolean;
}
export function useUserRole(): UserRole {
  const [userRole, setUserRole] = useState<UserRole>({
    role: "employee",
    canApproveLeave: false,
  });
  useEffect(() => {
    const checkUserRole = () => {
      const userStr = localStorage.getItem(STORAGE_KEYS.USER_DATA);
      if (userStr) {
        const user = JSON.parse(userStr);
        const role = user.role || "employee";

        const approvalRoles = [
          "Tenant Owner",
          "General Manager",
          "HR Manager",
          "Department Manager",
          "supervisor",
          "hr",
          "gm",
        ];

        const canApprove = approvalRoles.some(
          (approvalRole) => approvalRole.toLowerCase() === role.toLowerCase(),
        );

        const canApproveAtLevel = (level: string): boolean => {
          const roleHierarchy: Record<string, string[]> = {
            'Tenant Owner': ['department_manager', 'hr_manager', 'general_manager'],
            'General Manager': ['department_manager', 'hr_manager', 'general_manager'],
            'HR Manager': ['department_manager', 'hr_manager'],
            'Department Manager': ['department_manager']
          };

          const allowedLevels = roleHierarchy[role] || [];
          return allowedLevels.includes(level);
        };

        setUserRole({
          role,
          canApproveLeave: canApprove,
          canApproveAtLevel,
        });
      }
    };
    checkUserRole();

    window.addEventListener("storage", checkUserRole);
    return () => window.removeEventListener("storage", checkUserRole);
  }, []);
  return userRole;
}
