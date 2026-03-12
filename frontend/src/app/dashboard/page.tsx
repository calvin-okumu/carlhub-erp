import React from 'react';
import Link from 'next/link';
import Banner from '../../components/dashboard/Banner';
import DashboardFocusPanel from '../../components/dashboard/DashboardFocusPanel';
import DashboardSignals from '../../components/dashboard/DashboardSignals';
import FeatureGrid from '../../components/dashboard/FeatureGrid';

export default function Dashboard() {
    return (
        <div className="space-y-12 pb-12">
            <Banner />
            <section className="rounded-[26px] border border-slate-200/70 bg-white/80 p-6 shadow-[0_20px_55px_-40px_rgba(15,23,42,0.45)]">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">Quick actions</p>
                        <h2 className="font-display mt-2 text-xl font-semibold text-slate-900">Jump back in</h2>
                    </div>
                    <span className="rounded-full border border-slate-200/70 bg-slate-50 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500">
                        Suggested
                    </span>
                </div>
                <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {
                        [
                            { label: "Open projects", note: "Sprints + roadmap", href: "/dashboard/project-management" },
                            { label: "Add a client", note: "CRM accounts", href: "/dashboard/crm/clients" },
                            { label: "View contacts", note: "People directory", href: "/dashboard/contacts/contact-list" },
                            { label: "Review leave", note: "Requests queue", href: "/dashboard/leave" },
                        ].map((item) => (
                            <Link
                                key={item.label}
                                href={item.href}
                                className="group flex flex-col justify-between gap-3 rounded-[22px] border border-slate-200/70 bg-white/90 p-4 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-[0_18px_40px_-32px_rgba(15,23,42,0.45)]"
                            >
                                <span className="text-sm font-semibold text-slate-900">{item.label}</span>
                                <span className="text-xs uppercase tracking-[0.22em] text-slate-400">{item.note}</span>
                            </Link>
                        ))
                    }
                </div>
            </section>
            <div className="grid gap-10 xl:grid-cols-[minmax(0,1fr)_320px] xl:items-start">
                <FeatureGrid />
                <div className="space-y-6">
                    <DashboardFocusPanel />
                </div>
            </div>
            <DashboardSignals />
        </div>
    );
}
