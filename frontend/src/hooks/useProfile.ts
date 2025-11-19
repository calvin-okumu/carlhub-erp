import { useCallback, useEffect, useState } from "react";
import { getUserProfile, updateUserProfile } from '@/api/users';
import { User, UserProfile } from '@/api/types';
import { STORAGE_KEYS } from '@/constants/storage';

export function useProfile() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        const userStr = localStorage.getItem(STORAGE_KEYS.USER_DATA);
        if (!token) {
          throw new Error("No access token found. Please log in.");
        }
        if (!userStr) {
          throw new Error("No user data found. Please log in.");
        }
        const user = JSON.parse(userStr);
        const userProfile = await getUserProfile(token, user.id);
        setProfile(userProfile);
      } catch (err) {
        console.error("Error fetching profile:", err);
        setError(err instanceof Error ? err.message : "Failed to fetch profile. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const updateProfile = async (profileData: Partial<UserProfile>) => {
    try {
      setLoading(true);
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      const userStr = localStorage.getItem(STORAGE_KEYS.USER_DATA);
      if (!token || !userStr) {
        throw new Error("No access token or user data found");
      }
      const user = JSON.parse(userStr);
      await updateUserProfile(token, user.id, profileData);
      // Refetch profile
      const updatedProfile = await getUserProfile(token, user.id);
      setProfile(updatedProfile);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  return { profile, loading, error, updateProfile };
}