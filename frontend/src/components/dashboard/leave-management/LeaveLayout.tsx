import { ReactNode } from 'react';

interface LeaveLayoutProps {
    children: ReactNode;
}

export const LeaveLayout = ({ children }: LeaveLayoutProps) => {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            {children}
        </div>
    );
};