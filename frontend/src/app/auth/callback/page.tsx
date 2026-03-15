"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/api";
import { fetchMe } from "@/api/auth";

export default function AuthCallbackPage() {
    const router = useRouter();

    useEffect(() => {
        const fetchToken = async () => {
            try {
                const response = await fetch(`${API_BASE}/oauth/token/`, {
                    method: "GET",
                    credentials: "include",
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem("access_token", data.access);

                    // Fetch RBAC context from /api/me/
                    const me = await fetchMe(data.access);

                    localStorage.setItem("user", JSON.stringify({
                        id:          data.user_id,
                        email:       data.email,
                        first_name:  data.first_name,
                        last_name:   data.last_name,
                        role:        me?.role        ?? 'Employee',
                        is_owner:    me?.is_owner    ?? false,
                        is_approved: me?.is_approved ?? false,
                        tenant:      me?.tenant      ?? null,
                        tenant_name: me?.tenant_name ?? null,
                        department:  me?.department  ?? null,
                    }));
                    router.push("/dashboard");
                } else {
                    console.error("Failed to get token");
                    router.push("/login");
                }
            } catch (error) {
                console.error("Error fetching token:", error);
                router.push("/login");
            }
        };

        fetchToken();
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Completing authentication...</p>
            </div>
        </div>
    );
}
