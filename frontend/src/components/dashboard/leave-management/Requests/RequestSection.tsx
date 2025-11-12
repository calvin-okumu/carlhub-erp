"use client";
import LeaveRequestTable from './LeaveRequestTable';
import { RequestHeader } from './RequestHeader';
export const RequestSection = () => {
    return (
        <div>
            <RequestHeader
                onSearchChange={() => { }}
                onRequestSuccess={() => { }}
                onCreateRequest={() => { }}
            />
            <LeaveRequestTable
                onCreateRequest={() => { }}
                onEditRequest={() => { }}
                onDeleteRequest={() => { }}
            />
        </div>
    );
}
