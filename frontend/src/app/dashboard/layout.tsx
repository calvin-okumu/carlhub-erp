import React from 'react';
import Footer from '../../components/dashboard/Footer';
import Navbar from '../../components/layout/Navbar';
import Sidebar from '../../components/layout/Sidebar';
import AuthRefresh from '../../components/auth/AuthRefresh';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-[radial-gradient(1200px_circle_at_10%_-10%,rgba(59,130,246,0.18),transparent_55%),radial-gradient(900px_circle_at_90%_-5%,rgba(251,146,60,0.16),transparent_55%),linear-gradient(150deg,rgba(248,250,252,0.96)_0%,rgba(255,255,255,0.92)_50%,rgba(241,245,249,0.92)_100%)]">
            <div className="lg:grid lg:grid-cols-[300px_1fr]">
                <Sidebar />
                <div className="relative flex min-h-screen flex-col">
                    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(900px_circle_at_70%_10%,rgba(14,165,233,0.08),transparent_60%)]" />
                    <AuthRefresh />
                    <Navbar />
                    <main className="relative flex-1 px-4 pb-12 pt-8 sm:px-6 lg:px-10">
                        <div className="mx-auto w-full max-w-[1480px]">
                            {children}
                        </div>
                    </main>
                    <Footer />
                </div>
            </div>
        </div>
    );
}
