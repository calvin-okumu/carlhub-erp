import React, { useState } from 'react';

interface DropdownCardProps {
    title: string;
    children: React.ReactNode;
    className?: string;
}

export default function DropdownCard({ title, children, className = '' }: DropdownCardProps) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
            <div
                className="flex items-center justify-between cursor-pointer p-4 hover:bg-gray-50 transition-colors"
                onClick={() => setIsOpen(!isOpen)}
            >
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
                <div className={`transform transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>
                    <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </div>
            </div>

            <div className={`overflow-hidden transition-all duration-300 ${isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
                <div className="px-4 pb-4">{children}</div>
            </div>
        </div>
    );
}