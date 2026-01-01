import Pagination from '@/components/shared/Pagination';
import React from 'react';

interface TableProps {
    headers: { label: React.ReactNode; className?: string }[] | string[];
    rows: { key: string | number; data: React.ReactNode[] }[];
    className?: string;
    currentPage?: number;
    totalPages?: number;
    onPageChange?: (page: number) => void;
    itemsPerPage?: number;
    totalItems?: number;
}

export default function Table({
    headers,
    rows,
    className = '',
    currentPage,
    totalPages,
    onPageChange,
    itemsPerPage,
    totalItems
}: TableProps) {

    // Normalize headers
    const normalizedHeaders = headers.map((h) =>
        typeof h === "string" ? { label: h, className: "" } : h
    );

    // Per-column width constraints
    const columnWidths = [
        "max-w-[180px]",
        "max-w-[300px]",
        "max-w-[120px]",
        "max-w-[140px]",
        "max-w-[100px]",
        "max-w-[150px]"
    ];

    return (
        <div className={`overflow-x-auto ${className}`}>
            <table className="min-w-full table-fixed border-collapse">

                {/* HEADERS */}
                <thead className="bg-gray-50">
                    <tr>
                        {normalizedHeaders.map((header, index) => (
                            <th
                                key={index}
                                className={`
                                    px-4 py-3 
                                    text-left 
                                    text-sm 
                                    font-semibold 
                                    text-gray-700 
                                    uppercase 
                                    tracking-wider
                                    ${header.className || ""}
                                `}
                            >
                                {header.label}
                            </th>
                        ))}
                    </tr>
                </thead>

                {/* ROWS */}
                <tbody className="bg-white divide-y divide-gray-200">
                    {rows.map((row) => (
                        <tr key={row.key} className="hover:bg-gray-50">

                            {row.data.map((cell, index) => {
                                // If user manually provided <td>, don't nest
                                if (React.isValidElement(cell) && cell.type === 'td') {
                                    return React.cloneElement(cell, { key: index });
                                }

                                return (
                                    <td
                                        key={index}
                                        className={`
                                            px-4 py-4
                                            text-sm text-gray-900
                                            align-middle
                                            overflow-hidden
                                            text-ellipsis
                                            whitespace-nowrap
                                            ${columnWidths[index] || ""}
                                        `}
                                    >
                                        <div className="flex items-center gap-2 min-w-0">
                                            {cell}
                                        </div>
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* PAGINATION */}
            {currentPage && totalPages && onPageChange && (
                <div className="mt-4">
                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={onPageChange}
                        itemsPerPage={itemsPerPage || 10}
                        totalItems={totalItems || 0}
                    />
                </div>
            )}
        </div>
    );
}
