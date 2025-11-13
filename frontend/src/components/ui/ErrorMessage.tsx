interface ErrorMessageProps {
    message: string;
    type?: 'field' | 'general';
    className?: string;
}
export default function ErrorMessage({ message, type = 'field', className = '' }: ErrorMessageProps) {
    if (type === 'general') {
        return (
            <div className={`bg-red-50 border border-red-200 rounded-md p-3 ${className}`}>
                <p className="text-sm text-red-600">{message}</p>
            </div>
        );
    }

    return (
        <p className={`mt-1 text-sm text-red-600 ${className}`}>
            {message}
        </p>
    );
}
