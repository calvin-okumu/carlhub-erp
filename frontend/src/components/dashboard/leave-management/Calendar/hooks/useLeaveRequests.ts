import { useState, useEffect, useMemo, useRef } from 'react';
import { getLeaveRequests } from '../../../../../api/leave';
import type { LeaveRequest } from '../../../../../api/types';

interface UseLeaveRequestsParams {
  month?: number;
  year?: number;
  status?: string;
  employee?: number;
  page?: number;
  pageSize?: number;
}

// Simple cache to prevent duplicate API calls
const requestCache = new Map<string, { data: LeaveRequest[], timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const useLeaveRequests = (params?: UseLeaveRequestsParams) => {
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Memoize params to prevent unnecessary re-fetches
  const paramsKey = useMemo(() => {
    return params ? JSON.stringify(params) : '';
  }, [params]);

  useEffect(() => {
    // Cancel any previous requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const fetchLeaveRequests = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Check cache first
        const cached = requestCache.get(paramsKey);
        if (cached && (Date.now() - cached.timestamp) < CACHE_DURATION) {
          setLeaveRequests(cached.data);
          setIsLoading(false);
          return;
        }

        // Create new abort controller for this batch of requests
        abortControllerRef.current = new AbortController();

        // For calendar, we need both approved and taken leave requests
        // Make separate API calls since the backend doesn't accept comma-separated status
        const approvedRequests = await getLeaveRequests({
          ...params,
          status: 'approved'
        });

        const takenRequests = await getLeaveRequests({
          ...params,
          status: 'taken'
        });

        // Combine the results
        const approvedData = approvedRequests.results || approvedRequests;
        const takenData = takenRequests.results || takenRequests;
        const combinedData = [...approvedData, ...takenData];

        // Cache the result
        requestCache.set(paramsKey, { data: combinedData, timestamp: Date.now() });

        setLeaveRequests(combinedData);
      } catch (err) {
        // Don't set error if request was aborted
        if (err instanceof Error && err.name === 'AbortError') {
          return;
        }

        let errorMessage = 'Failed to fetch leave requests';
        if (err instanceof Error) {
          // Handle throttling errors specifically
          if (err.message.includes('throttled') || err.message.includes('rate limit')) {
            errorMessage = 'Too many requests. Please wait a moment before trying again.';
          } else {
            errorMessage = err.message;
          }
        }
        setError(errorMessage);
        console.error('Error fetching leave requests:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaveRequests();

    // Cleanup function to abort request on unmount or param change
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [paramsKey, params]);

  const refetch = () => {
    // Clear cache for this specific request
    requestCache.delete(paramsKey);

    setIsLoading(true);
    setError(null);

    const fetchLeaveRequests = async () => {
      try {
        // Create new abort controller for this batch of requests
        abortControllerRef.current = new AbortController();

        // For calendar, we need both approved and taken leave requests
        const approvedRequests = await getLeaveRequests({
          ...params,
          status: 'approved'
        });

        const takenRequests = await getLeaveRequests({
          ...params,
          status: 'taken'
        });

        // Combine the results
        const approvedData = approvedRequests.results || approvedRequests;
        const takenData = takenRequests.results || takenRequests;
        const combinedData = [...approvedData, ...takenData];

        // Cache the result
        requestCache.set(paramsKey, { data: combinedData, timestamp: Date.now() });

        setLeaveRequests(combinedData);
      } catch (err) {
        // Don't set error if request was aborted
        if (err instanceof Error && err.name === 'AbortError') {
          return;
        }

        let errorMessage = 'Failed to fetch leave requests';
        if (err instanceof Error) {
          if (err.message.includes('throttled') || err.message.includes('rate limit')) {
            errorMessage = 'Too many requests. Please wait a moment before trying again.';
          } else {
            errorMessage = err.message;
          }
        }
        setError(errorMessage);
        console.error('Error fetching leave requests:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLeaveRequests();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    leaveRequests,
    isLoading,
    error,
    refetch,
  };
};