import React from 'react';
import Table from '@/components/ui/Table';
import Button from '@/components/ui/Button';
import StatusBadge from '@/components/ui/StatusBadge';

interface Employee {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    phone?: string;
    job_title?: string;
    hire_date?: string;
    is_active?: boolean;
}

interface TerminatedEmployeeTableProps {
    searchTerm: string;
    entriesPerPage: number;
    currentPage: number;
    employees?: Employee[];
    totalPages?: number;
    onPageChange?: (page: number) => void;
    itemsPerPage?: number;
    totalItems?: number;
    onReactivateEmployee?: (employee: Employee) => void;
    onDeleteEmployee?: (employee: Employee) => void;
}

export default function TerminatedEmployeeTable({ searchTerm, entriesPerPage, currentPage, employees = [], totalPages, onPageChange, itemsPerPage, totalItems, onReactivateEmployee, onDeleteEmployee }: TerminatedEmployeeTableProps) {
    const filteredEmployees = employees.filter(emp =>
        `${emp.first_name} ${emp.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const startIndex = (currentPage - 1) * entriesPerPage;
    const paginatedEmployees = filteredEmployees.slice(startIndex, startIndex + entriesPerPage);

    if (filteredEmployees.length === 0) {
        return (
            <div className="text-center py-8">
                <p className="text-gray-500">No terminated employees</p>
            </div>
        );
    }

    const headers = ['Employee', 'Job Title', 'Email', 'Phone', 'Termination Date', 'Status', 'Actions'];

    const rows = paginatedEmployees.map(emp => ({
        key: emp.id,
        data: [
            <div key="employee" className="flex items-center">
                <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center text-white text-sm font-medium mr-3">
                    {emp.first_name?.[0]}{emp.last_name?.[0]}
                </div>
                {emp.first_name} {emp.last_name}
            </div>,
            emp.job_title || 'N/A',
            emp.email,
            emp.phone || 'N/A',
            emp.hire_date ? new Date(emp.hire_date).toLocaleDateString() : 'N/A',
            <StatusBadge key="status" status="terminated" />,
            <div key="actions" className="flex gap-2">
                <Button
                    onClick={() => onReactivateEmployee?.(emp)}
                    className="bg-green-600 text-white"
                    size="sm"
                >
                    Reactivate
                </Button>
                 <Button
                     onClick={() => {
                         if (confirm('Are you sure you want to permanently delete this employee? This action cannot be undone.')) {
                             onDeleteEmployee?.(emp);
                         }
                     }}
                     className="bg-red-600 text-white"
                     size="sm"
                 >
                     Delete
                 </Button>
            </div>,
        ],
    }));

    return <Table headers={headers} rows={rows} currentPage={currentPage} totalPages={totalPages} onPageChange={onPageChange} itemsPerPage={entriesPerPage} totalItems={totalItems} />;
}