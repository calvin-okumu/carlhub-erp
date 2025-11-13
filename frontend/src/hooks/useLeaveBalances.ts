import { useState, useEffect } from 'react';
import { getLeaveBalances, type LeaveBalance } from '../api';

export const useLeaveBalances = (year?: number) => {
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBalances = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const params = year ? { year } : undefined;
        const response = await getLeaveBalances(params);

        // Assuming the API returns results directly, not paginated for balances
        // If paginated, we might want to get all results
        setBalances(response.results || response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch leave balances');
        console.error('Error fetching leave balances:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBalances();
  }, [year]);

  const refetch = () => {
    setIsLoading(true);
    setError(null);
    // Re-trigger the effect by updating a dependency
    // This is a simple approach - in production you might want a more sophisticated solution
    const fetchBalances = async () => {
      try {
        const params = year ? { year } : undefined;
        const response = await getLeaveBalances(params);
        setBalances(response.results || response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch leave balances');
      } finally {
        setIsLoading(false);
      }
    };
    fetchBalances();
  };

  return {
    balances,
    isLoading,
    error,
    refetch,
  };
};