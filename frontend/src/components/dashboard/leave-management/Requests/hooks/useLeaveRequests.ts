import { useCallback, useEffect, useMemo, useState } from 'react';
import { getLeaveRequests } from '../../../../../api/leave';
import type { LeaveRequest, PaginatedResponse } from '../../../../../api/types';

type LeaveType = 'all' | 'annual_leave' | 'sick_leave' | 'personal_leave' | 'maternity_leave' | 'emergency_leave' | 'unpaid_leave';

interface UseLeaveRequestsOptions {
  searchTerm?: string;
  sortBy?: LeaveType;
  pageSize?: number;
}

export const useLeaveRequests = ({ searchTerm = '', sortBy = 'all', pageSize = 10 }: UseLeaveRequestsOptions = {}) => {
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchRequests = useCallback(async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const response: PaginatedResponse<LeaveRequest> = await getLeaveRequests({
        page,
        page_size: pageSize
      });
      setRequests(response.results);
      setTotalPages(Math.ceil(response.count / pageSize));
      setTotalItems(response.count);
    } catch (err) {
      setError('Failed to fetch leave requests');
      console.error('Failed to fetch leave requests:', err);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  const filteredRequests = useMemo(() => {
    let filtered = requests;

    if (searchTerm) {
      filtered = filtered.filter(request =>
        request.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        request.leave_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        request.status.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (sortBy && sortBy !== 'all') {
      filtered = filtered.filter(request => request.leave_type === sortBy);
    }

    return filtered;
  }, [requests, searchTerm, sortBy]);

  useEffect(() => {
    fetchRequests(1);
  }, [fetchRequests]);

  return {
    requests: filteredRequests,
    loading,
    error,
    currentPage,
    totalPages,
    totalItems,
    refetch: () => fetchRequests(currentPage),
    setPage: setCurrentPage
  };
};