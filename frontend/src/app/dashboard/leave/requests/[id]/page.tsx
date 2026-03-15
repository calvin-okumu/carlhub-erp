"use client";

import { getLeaveRequest, approveLeaveRequest, rejectLeaveRequest, cancelLeaveRequest } from "@/api/leave";
import type { LeaveRequest } from "@/api/types";
import { LeaveLayout } from "@/components/dashboard/leave-management/LeaveLayout";
import Loader from "@/components/shared/Loader";
import Button from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function LeaveRequestDetailPage() {
    const params = useParams();
    const router = useRouter();
    const id = Array.isArray(params.id) ? params.id[0] : (params.id as string);
    const [request, setRequest] = useState<LeaveRequest | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [actionLoading, setActionLoading] = useState(false);
    const { can } = useAuth();

    useEffect(() => {
        if (!id) return;
        const fetchRequest = async () => {
            setLoading(true);
            try {
                const data = await getLeaveRequest(id);
                setRequest(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load leave request.");
            } finally {
                setLoading(false);
            }
        };
        fetchRequest();
    }, [id]);

    const handleApprove = async () => {
        if (!id) return;
        setActionLoading(true);
        try {
            const updated = await approveLeaveRequest(id);
            setRequest(updated);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to approve request.");
        } finally {
            setActionLoading(false);
        }
    };

    const handleReject = async () => {
        if (!id) return;
        setActionLoading(true);
        try {
            const updated = await rejectLeaveRequest(id);
            setRequest(updated);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to reject request.");
        } finally {
            setActionLoading(false);
        }
    };

    const handleCancel = async () => {
        if (!id || !confirm("Cancel this leave request?")) return;
        setActionLoading(true);
        try {
            const updated = await cancelLeaveRequest(id);
            setRequest(updated);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to cancel request.");
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) return <Loader />;
    if (error) return <div className="p-6 text-red-500">{error}</div>;
    if (!request) return <div className="p-6 text-gray-500">Leave request not found.</div>;

    const isPending = request.status?.toLowerCase().includes("pending");

    return (
        <LeaveLayout>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Leave Management</p>
                        <h1 className="h1-title">Leave Request Details</h1>
                    </div>
                    <Button variant="outline" onClick={() => router.push("/dashboard/leave/requests")}>
                        Back to Requests
                    </Button>
                </div>

                <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-6 shadow-sm space-y-4">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Leave Type</p>
                            <p className="mt-1 text-sm text-slate-800">{request.leave_type}</p>
                        </div>
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Status</p>
                            <p className="mt-1 text-sm font-semibold text-slate-800 capitalize">{request.status?.replace(/_/g, ' ')}</p>
                        </div>
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Start Date</p>
                            <p className="mt-1 text-sm text-slate-800">{request.start_date}</p>
                        </div>
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">End Date</p>
                            <p className="mt-1 text-sm text-slate-800">{request.end_date}</p>
                        </div>
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Days Requested</p>
                            <p className="mt-1 text-sm text-slate-800">{request.days_requested}</p>
                        </div>
                        {request.reason && (
                            <div className="sm:col-span-2">
                                <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Reason</p>
                                <p className="mt-1 text-sm text-slate-800">{request.reason}</p>
                            </div>
                        )}
                    </div>
                </div>

                {isPending && (
                    <div className="flex gap-3">
                        {can('approve_leave') && (
                            <Button onClick={handleApprove} disabled={actionLoading}>
                                Approve
                            </Button>
                        )}
                        {can('approve_leave') && (
                            <Button variant="danger" onClick={handleReject} disabled={actionLoading}>
                                Reject
                            </Button>
                        )}
                        <Button variant="outline" onClick={handleCancel} disabled={actionLoading}>
                            Cancel Request
                        </Button>
                    </div>
                )}
            </div>
        </LeaveLayout>
    );
}
