import { useEffect, useState } from "react";
interface UserRole {
  role: string;
  canApproveLeave: boolean;
}
export function useUserRole(): UserRole {
  const [userRole, setUserRole] = useState<UserRole>({
    role: "employee",
    canApproveLeave: false,
  });
  useEffect(() => {
    const checkUserRole = () => {
      const userStr = localStorage.getItem("user");
      if (userStr) {
        const user = JSON.parse(userStr);
        const role = user.role || "employee";

        const approvalRoles = [
          "Tenant Owner",
          "Manager",
          "admin",
          "owner",
          "supervisor",
          "department_manager",
          "hr",
          "gm",
        ];

        const canApprove = approvalRoles.some(approvalRole =>
          approvalRole.toLowerCase() === role.toLowerCase()
        );

        setUserRole({
          role,
          canApproveLeave: canApprove,
        });
      }
    };
    checkUserRole();

    window.addEventListener("storage", checkUserRole);
    return () => window.removeEventListener("storage", checkUserRole);
  }, []);
  return userRole;
}
