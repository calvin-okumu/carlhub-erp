"use client";

import { useEffect, useRef } from "react";
import { refreshAccessToken } from "@/api";

const REFRESH_BUFFER_MS = 60 * 1000;

const decodeExpiry = (token: string): number | null => {
  const parts = token.split(".");
  if (parts.length < 2) return null;

  const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");

  try {
    const payload = JSON.parse(atob(padded));
    if (typeof payload.exp !== "number") return null;
    return payload.exp * 1000;
  } catch {
    return null;
  }
};

export default function AuthRefresh() {
  const timerRef = useRef<number | null>(null);
  const refreshingRef = useRef<Promise<string | null> | null>(null);

  useEffect(() => {
    const clearTimer = () => {
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };

    const scheduleRefresh = (token: string) => {
      clearTimer();
      const expiry = decodeExpiry(token);
      if (!expiry) return;

      const delay = Math.max(expiry - Date.now() - REFRESH_BUFFER_MS, 0);
      timerRef.current = window.setTimeout(async () => {
        if (!refreshingRef.current) {
          refreshingRef.current = refreshAccessToken();
        }
        const refreshed = await refreshingRef.current;
        refreshingRef.current = null;

        if (refreshed) {
          scheduleRefresh(refreshed);
        }
      }, delay);
    };

    const kick = () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      scheduleRefresh(token);
    };

    const handleStorage = (event: StorageEvent) => {
      if (event.key === "access_token") {
        const token = event.newValue;
        if (token) {
          scheduleRefresh(token);
        } else {
          clearTimer();
        }
      }
    };

    kick();
    window.addEventListener("storage", handleStorage);

    return () => {
      clearTimer();
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  return null;
}
