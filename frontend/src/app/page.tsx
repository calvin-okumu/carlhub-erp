"use client";

import Features from "@/components/website/Features";
import Footer from "@/components/website/Footer";
import Header from "@/components/website/Header";
import Hero from "@/components/website/Hero";
import KeyFeatures from "@/components/website/KeyFeatures";
import Pricing from "@/components/website/Pricing";
import WhySkhokho from "@/components/website/WhySkhokho";
import { refreshAccessToken } from "@/api";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Home() {
    const router = useRouter();
    const [checkingSession, setCheckingSession] = useState(true);

    useEffect(() => {
        const bootstrapAuth = async () => {
            const token = localStorage.getItem("access_token");
            if (token) {
                router.replace("/dashboard");
                return;
            }

            const refreshed = await refreshAccessToken();
            if (refreshed) {
                router.replace("/dashboard");
                return;
            }

            router.replace("/login");
        };

        bootstrapAuth();
    }, [router]);

    if (checkingSession) {
        return null;
    }

    return null;
}
