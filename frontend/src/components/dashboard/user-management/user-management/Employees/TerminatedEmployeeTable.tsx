import React from 'react';
import Table from '@/components/ui/Table';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';

interface Employee {
    id: number;
    name: string;
    avatar: string;
    jobTitle: string;
    email: string;
    phone: string;
    employmentDate: string;
    status: string;
}

interface TerminatedEmployeeTableProps {
    searchTerm: string;
    entriesPerPage: number;
    currentPage: number;
    employees?: Employee[];
    onPageChange: (page: number) => void;
}

export default function TerminatedEmployeeTable({ searchTerm, entriesPerPage, currentPage, employees = [], onPageChange }: TerminatedEmployeeTableProps) {
    const filteredEmployees = employees.filter(emp =>
        emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const totalItems = filteredEmployees.length;
    const totalPages = Math.ceil(totalItems / entriesPerPage);
    const startIndex = (currentPage - 1) * entriesPerPage;
    const paginatedEmployees = filteredEmployees.slice(startIndex, startIndex + entriesPerPage);

    const headers = ['Employee', 'Job Title', 'Email', 'Phone', 'Employment Date', 'Status', 'View', 'Actions'];

    const rows = paginatedEmployees.map(emp => ({
        key: emp.id,
        data: [
            <div key="employee" className="flex items-center">
                <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center text-white text-sm font-medium mr-3">
                    {emp.avatar}
                </div>
                {emp.name}
            </div>,
            emp.jobTitle,
            emp.email,
            emp.phone,
            emp.employmentDate,
            <StatusBadge key="status" status={emp.status} />,
            <Button key="view" className="bg-blue-600 text-white">View Employee</Button>,
            <Button key="terminate" className="bg-red-600 text-white">Terminate</Button>,
        ],
    }));

    return <Table headers={headers} rows={rows} currentPage={currentPage} totalPages={totalPages} onPageChange={onPageChange} itemsPerPage={entriesPerPage} totalItems={totalItems} />;
}