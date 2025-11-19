"use client";

import { API_BASE } from "@/api";
import { STORAGE_KEYS } from "@/constants/storage";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthCallbackPage() {
    const router = useRouter();

    useEffect(() => {
        const fetchToken = async () => {
            try {
                const response = await fetch(`${API_BASE}/get-token/`, {
                    method: "GET",
                    credentials: "include",
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.token);
                    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh);
                    localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify({
                        id: data.user_id,
                        username: data.username,
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
