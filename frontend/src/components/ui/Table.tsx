import React from 'react';
import Pagination from '@/components/shared/Pagination';

interface TableProps {
    headers: string[];
    rows: { key: string | number; data: (string | number | React.ReactNode)[] }[];
    className?: string;
    currentPage?: number;
    totalPages?: number;
    onPageChange?: (page: number) => void;
    itemsPerPage?: number;
    totalItems?: number;
}

export default function Table({ headers, rows, className = '', currentPage, totalPages, onPageChange, itemsPerPage, totalItems }: TableProps) {
   return (
     <div className={`overflow-x-auto ${className}`}>
       <table className="min-w-full divide-y divide-gray-200">
         <thead className="bg-gray-50">
           <tr>
              {headers.map((header, index) => (
                <th
                  key={index}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {header}
                </th>
              ))}
           </tr>
         </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rows.map((row) => (
              <tr key={row.key} className="hover:bg-gray-50">
                {row.data.map((cell, cellIndex) => (
                   <td key={cellIndex} className="px-4 py-4 truncate max-w-xs text-sm text-gray-900">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
       </table>
       {currentPage && totalPages && onPageChange && itemsPerPage && totalItems && (
         <div className="mt-4">
           <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={onPageChange} itemsPerPage={itemsPerPage} totalItems={totalItems} />
         </div>
       )}
     </div>
   );
}