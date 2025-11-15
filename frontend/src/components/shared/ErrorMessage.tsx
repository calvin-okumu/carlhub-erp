
import { useState } from 'react';

interface ErrorMessageProps {
    message: string;
    type?: 'field' | 'general';
    className?: string;
}

export default function ErrorMessage({ message, type = 'field', className = '' }: ErrorMessageProps) {
    const [visible, setVisible] = useState(true);

    if (!visible) return null;

    const handleClose = () => setVisible(false);

    if (type === 'general') {
        return (
            <div className={`bg-red-50 border border-red-200 rounded-md p-3 flex justify-between items-start ${className}`}>
                <p className="text-sm text-red-600">{message}</p>
                <button
                    onClick={handleClose}
                    className="ml-4 text-red-400 hover:text-red-600 font-bold"
                    aria-label="Close error"
                >
                    ×
                </button>
            </div>
        );
    }

    return (
        <p className={`mt-1 text-sm text-red-600 flex justify-between items-center ${className}`}>
            {message}
            <button
                onClick={handleClose}
                className="ml-2 text-red-400 hover:text-red-600 font-bold"
                aria-label="Close error"
            >
                ×
            </button>
        </p>
    );
}
