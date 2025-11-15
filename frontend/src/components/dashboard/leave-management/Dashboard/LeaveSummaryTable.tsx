import { getLeaveRequests } from '@/api/leave';
import type { LeaveRequest } from '@/api/types';
import Loader from '@/components/shared/Loader';
import Card from '@/components/ui/Card';
import { FileText } from 'lucide-react';
import Table from '@/components/ui/Table';
import { useEffect, useState } from 'react';

export const LeaveSummaryTable = () => {
    const [requests, setRequests] = useState<LeaveRequest[]>([]);
    const [loading, setLoading] = useState(true);

    const formatLeaveType = (leaveType: string) => {
        return leaveType.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                // Get current user ID from localStorage
                const userData = localStorage.getItem('user');
                let employeeId: number | undefined;

                if (userData) {
                    const user = JSON.parse(userData);
                    employeeId = user.id;
                }

                const data = await getLeaveRequests({
                    page_size: 5,
                    employee: employeeId
                });

                if (data && typeof data === 'object' && 'results' in data) {
                    setRequests(data.results);
                } else {
                    setRequests(data as LeaveRequest[]);
                }
            } catch (error) {
                console.error('Failed to fetch leave summary:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, []);

    if (loading) {
        return <Loader />;
    }

    const headers = ['Employee', 'Type', 'Status', 'Start Date', 'End Date'];

    const rows = requests.map((request) => ({
        key: request.id,
        data: [
            request.employee_name || 'Unknown',
            formatLeaveType(request.leave_type) || 'N/A',
            request.status,
            new Date(request.start_date).toLocaleDateString(),
            new Date(request.end_date).toLocaleDateString(),
        ],
    }));

    return (
        <div className="mt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Leave Requests</h3>
            <Card>
                {rows.length === 0 ? (
                    <div className="text-center py-8">
                        <FileText className="mx-auto h-12 w-12 text-gray-400" />
                        <p className="text-gray-500 text-sm">No leave requests found</p>
                    </div>
                ) : (
                    <Table headers={headers} rows={rows} />
                )}
            </Card>
        </div>
    );
};
