import { useState, useEffect } from 'react';
import { getCurrentUser } from '@/api/users';
import { User } from '@/api/types';

export function useProfile() {
  const [profile, setProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const userStr = localStorage.getItem("user");
        if (!token) {
          throw new Error("No access token found. Please log in.");
        }
        if (!userStr) {
          throw new Error("No user data found. Please log in.");
        }
        const user = await getCurrentUser(token);
        setProfile(user);
      } catch (err) {
        console.error("Error fetching profile:", err);
        setError(err instanceof Error ? err.message : "Failed to fetch profile. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  return { profile, loading, error };
}