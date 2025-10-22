import React from 'react';
import Link from 'next/link';

export default function Footer() {
    return (
        <footer className="bg-white border-t border-gray-200 shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <div className="text-center text-sm text-gray-500">
                    © 2025, powered by{' '}
                    <Link href="#" className="text-blue-600 hover:text-blue-800 font-medium">
                        Carlhub
                    </Link>
                </div>
            </div>
        </footer>
    );
}
