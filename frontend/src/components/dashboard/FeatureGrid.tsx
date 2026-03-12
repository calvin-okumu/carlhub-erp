
"use client";

import {
    Archive,
    BarChart3,
    Building,
    Calendar,
    DollarSign,
    FolderOpen,
    TrendingUp,
    UserCheck,
    Users,
} from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

const features = [
    {
        title: "Contact Management",
        subtitle: "Organize and manage all your contacts",
        icon: Users,
        color: "bg-emerald-500/90",
        glow: "from-emerald-500/18 via-emerald-500/0",
        accent: "text-emerald-600",
        badge: "Core",
        meta: "1,284 contacts",
        buttonColor: "bg-emerald-500/90 hover:bg-emerald-600",
        cta: "View Contacts",
        href: "/dashboard/contacts/contact-list",
        active: true,
        size: "md:col-span-2",
    },
    {
        title: "Customer Relations(CRM)",
        subtitle: "Build stronger customer relationships",
        icon: UserCheck,
        color: "bg-amber-500/90",
        glow: "from-amber-500/18 via-amber-500/0",
        accent: "text-amber-600",
        badge: "Revenue",
        meta: "34 active deals",
        buttonColor: "bg-amber-500/90 hover:bg-amber-600",
        cta: "View CRM",
        href: "/dashboard/crm/clients",
        active: true,
        size: "",
    },
    {
        title: "Vendor Management",
        subtitle: "Manage suppliers and vendors efficiently",
        icon: Building,
        color: "bg-sky-500/90",
        glow: "from-sky-500/18 via-sky-500/0",
        accent: "text-sky-600",
        badge: "Supply",
        meta: "18 vendors",
        buttonColor: "bg-sky-500/90 hover:bg-sky-600",
        cta: "View Vendors",
        href: "/dashboard/vendors/vendor-list",
        active: true,
        size: "",
    },
    {
        title: "Financial Management",
        subtitle: "Handle finances and accounting",
        icon: DollarSign,
        color: "bg-rose-500/90",
        glow: "from-rose-500/18 via-rose-500/0",
        accent: "text-rose-600",
        badge: "Finance",
        meta: "6 ledgers",
        buttonColor: "bg-rose-500/90 hover:bg-rose-600",
        cta: "View Finance",
        href: "/dashboard/finance/accounts",
        active: true,
        size: "md:row-span-2",
    },
    {
        title: "Asset Management",
        subtitle: "Track and manage company assets",
        icon: Archive,
        color: "bg-slate-600/90",
        glow: "from-slate-500/18 via-slate-500/0",
        accent: "text-slate-600",
        badge: "Inventory",
        meta: "92 assets",
        buttonColor: "bg-slate-700/90 hover:bg-slate-800",
        cta: "View Assets",
        href: "/dashboard/assets/products",
        active: true,
        size: "",
    },
    {
        title: "Project Management",
        subtitle: "Plan and track project progress",
        icon: FolderOpen,
        color: "bg-lime-500/90",
        glow: "from-lime-500/18 via-lime-500/0",
        accent: "text-lime-600",
        badge: "Delivery",
        meta: "12 milestones",
        buttonColor: "bg-lime-500/90 hover:bg-lime-600",
        cta: "View Projects",
        href: "/dashboard/project-management/",
        active: true,
        size: "",
    },
    {
        title: "Business Intelligence",
        subtitle: "Advanced analytics and insights",
        icon: TrendingUp,
        color: "bg-teal-500/90",
        glow: "from-teal-500/18 via-teal-500/0",
        accent: "text-teal-600",
        badge: "Labs",
        meta: "Early access",
        buttonColor: "",
        cta: "Coming Soon",
        href: "#",
        active: false,
        size: "",
    },
    {
        title: "Reports & Analytics",
        subtitle: "Generate reports and visualize data",
        icon: BarChart3,
        color: "bg-orange-500/90",
        glow: "from-orange-500/18 via-orange-500/0",
        accent: "text-orange-600",
        badge: "Studio",
        meta: "Charts and exports",
        buttonColor: "",
        cta: "Coming Soon",
        href: "#",
        active: false,
        size: "",
    },
    {
        title: "Leave Management",
        subtitle: "Manage employee leave and absences",
        icon: Calendar,
        color: "bg-cyan-600/90",
        glow: "from-cyan-500/18 via-cyan-500/0",
        accent: "text-cyan-600",
        badge: "People",
        meta: "8 requests",
        buttonColor: "bg-cyan-600/90 hover:bg-cyan-700",
        cta: "View Leave",
        href: "/dashboard/leave/",
        active: true,
        size: "xl:col-span-2",
    },
];

export default function FeatureGrid() {
    const searchParams = useSearchParams();
    const [showAll, setShowAll] = useState(false);
    const [pageIndex, setPageIndex] = useState(0);
    const query = searchParams.get('search') || '';
    const activeFeatures = features.filter((feature) => feature.active);
    const normalizedQuery = query.trim().toLowerCase();
    const filteredFeatures = features.filter(
        (feature) =>
            !normalizedQuery ||
            feature.title.toLowerCase().includes(normalizedQuery) ||
            feature.subtitle.toLowerCase().includes(normalizedQuery)
    );
    const pageSize = 3;
    const maxPage = Math.max(0, Math.ceil(activeFeatures.length / pageSize) - 1);
    const visibleFeatures = normalizedQuery
        ? filteredFeatures
        : showAll
            ? activeFeatures
            : activeFeatures.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize);
    const countLabel = normalizedQuery ? "matches" : "active apps";
    const countValue = normalizedQuery ? visibleFeatures.length : activeFeatures.length;

    useEffect(() => {
        setPageIndex(0);
    }, [normalizedQuery, showAll]);

    return (
        <section id="apps" className="space-y-8">
            <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.32em] text-slate-500">Workspace map</p>
                    <h2 className="font-display mt-2 text-2xl font-semibold text-slate-900 md:text-3xl">
                        Choose the lane that needs you next
                    </h2>
                    <p className="mt-2 max-w-2xl text-sm text-slate-600 md:text-base">
                        Every module has a different pace. Step into a lane to orchestrate workflows, surface context, and keep momentum strong.
                        Active apps stay in focus; search reveals upcoming modules.
                    </p>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-3 rounded-[22px] border border-slate-200/60 bg-white/70 px-4 py-3 text-sm text-slate-600 shadow-sm">
                        <span className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
                            {normalizedQuery ? "Showing" : "Active"}
                        </span>
                        <span className="text-lg font-semibold text-slate-900">{countValue}</span>
                        <span>{countLabel}</span>
                    </div>
                    {!normalizedQuery && !showAll && activeFeatures.length > pageSize && (
                        <div className="hidden items-center gap-2 lg:flex">
                        <button
                            type="button"
                            onClick={() => setPageIndex((prev) => Math.max(0, prev - 1))}
                            className="rounded-full border border-slate-200/70 bg-white px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
                            aria-label="Scroll apps left"
                            disabled={pageIndex === 0}
                        >
                            Prev
                        </button>
                        <button
                            type="button"
                            onClick={() => setPageIndex((prev) => Math.min(maxPage, prev + 1))}
                            className="rounded-full border border-slate-200/70 bg-white px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600 disabled:cursor-not-allowed disabled:opacity-40"
                            aria-label="Scroll apps right"
                            disabled={pageIndex >= maxPage}
                        >
                            Next
                        </button>
                        </div>
                    )}
                </div>
            </div>
            {visibleFeatures.length === 0 ? (
                <div className="rounded-[28px] border border-dashed border-slate-300/70 bg-white/70 py-20 text-center shadow-sm">
                    <p className="text-base text-slate-500">No apps found matching &ldquo;{query}&rdquo;</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6 md:auto-rows-fr md:grid-cols-2 xl:grid-cols-3">
                    {visibleFeatures.map((feature) => (
                        <div
                            key={feature.title}
                            className="group relative flex h-full min-h-[240px] flex-col overflow-hidden rounded-[28px] border border-slate-200/70 bg-white/85 p-6 shadow-[0_24px_60px_-45px_rgba(15,23,42,0.65)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_36px_80px_-50px_rgba(15,23,42,0.8)]"
                        >
                            <div className={`absolute inset-0 bg-gradient-to-br ${feature.glow} to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100`} />
                            <div className="relative flex items-start justify-between">
                                <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${feature.color} shadow-lg shadow-black/10 transition-transform duration-300 group-hover:scale-105`}>
                                    <feature.icon className="h-7 w-7 text-white" />
                                </div>
                                <div className="flex flex-col items-end gap-2">
                                    <span className="rounded-full border border-slate-200/70 bg-white/80 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500">
                                        {feature.badge}
                                    </span>
                                    {!feature.active && (
                                        <span className="rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500">
                                            Soon
                                        </span>
                                    )}
                                </div>
                            </div>

                            <div className="relative mt-5 flex-1">
                                <h3 className="font-display text-xl font-semibold text-slate-900">
                                    {feature.title}
                                </h3>
                                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                                    {feature.subtitle}
                                </p>
                            </div>

                            <div className="relative mt-6 flex items-center justify-between gap-3">
                                <span className={`text-xs font-semibold uppercase tracking-[0.25em] ${feature.accent}`}>
                                    {feature.meta}
                                </span>
                                {feature.active ? (
                                    <Link
                                        href={feature.href}
                                        className={`inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-white shadow-md transition-all duration-300 hover:shadow-lg ${feature.buttonColor}`}
                                    >
                                        {feature.cta}
                                    </Link>
                                ) : (
                                    <button
                                        disabled
                                        aria-disabled="true"
                                        className="rounded-full border border-slate-200 bg-slate-100 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-slate-400"
                                    >
                                        {feature.cta}
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
            {!normalizedQuery && activeFeatures.length > 4 && (
                <button
                    type="button"
                    onClick={() => setShowAll((prev) => !prev)}
                    className="inline-flex items-center justify-center rounded-full border border-slate-200/70 bg-white px-5 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600"
                >
                    {showAll ? "Show fewer apps" : `Show all ${activeFeatures.length} apps`}
                </button>
            )}
        </section>
    );
}
