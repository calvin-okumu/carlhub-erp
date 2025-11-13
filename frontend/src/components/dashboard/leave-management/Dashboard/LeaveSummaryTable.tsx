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

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const data = await getLeaveRequests({ limit: 5 });
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
            request.leave_type || 'N/A',
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
