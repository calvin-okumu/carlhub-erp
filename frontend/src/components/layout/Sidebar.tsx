"use client";

import {
    Archive,
    BadgeCheck,
    BarChart3,
    Building2,
    Calendar,
    CalendarClock,
    ChevronDown,
    Database,
    FileText,
    FolderKanban,
    LayoutDashboard,
    LifeBuoy,
    LineChart,
    Menu,
    MessagesSquare,
    NotebookPen,
    Receipt,
    ShieldCheck,
    Sparkles,
    UserCheck,
    Users,
    Wallet,
    Workflow,
    X,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

type NavItem = {
    name: string;
    href: string;
    icon: typeof LayoutDashboard;
    description?: string;
    badge?: string;
    match?: "exact" | "prefix";
};

const primaryItems: NavItem[] = [
    {
        name: "Project Hub",
        href: "/dashboard/project-management",
        icon: FolderKanban,
        description: "Plans and sprints",
        match: "prefix",
    },
    {
        name: "Workspace Chat",
        href: "/chat",
        icon: MessagesSquare,
        description: "Team threads",
    },
];

const growthItems: NavItem[] = [
    {
        name: "CRM Clients",
        href: "/dashboard/crm/clients",
        icon: BadgeCheck,
        description: "Accounts and health",
        badge: "Core",
    },
    {
        name: "Marketing",
        href: "/dashboard/crm/marketing",
        icon: LineChart,
        description: "Campaign signals",
    },
    {
        name: "Campaigns",
        href: "/dashboard/crm/campaigns",
        icon: Sparkles,
        description: "Nurture flows",
    },
    {
        name: "Sales",
        href: "/dashboard/crm/sales",
        icon: Workflow,
        description: "Forecast and deals",
    },
    {
        name: "Sales Funnel",
        href: "/dashboard/crm/sales-funnel",
        icon: BarChart3,
        description: "Conversion view",
    },
];

const operationsItems: NavItem[] = [
    {
        name: "Contact List",
        href: "/dashboard/contacts/contact-list",
        icon: Users,
        description: "People directory",
    },
    {
        name: "Contact Groups",
        href: "/dashboard/contacts/contact-group",
        icon: UserCheck,
        description: "Segments",
    },
    {
        name: "Tickets",
        href: "/dashboard/tickets",
        icon: LifeBuoy,
        description: "Support queue",
    },
    {
        name: "Vendors",
        href: "/dashboard/vendors/vendor-list",
        icon: Building2,
        description: "Suppliers",
    },
];

const financeItems: NavItem[] = [
    {
        name: "Accounts",
        href: "/dashboard/finance/accounts",
        icon: Wallet,
        description: "Ledgers",
    },
    {
        name: "Quotes",
        href: "/dashboard/finance/quotes",
        icon: FileText,
        description: "Estimates",
    },
    {
        name: "Invoices",
        href: "/dashboard/finance/invoices",
        icon: Receipt,
        description: "Billing",
    },
    {
        name: "Expenses",
        href: "/dashboard/finance/expenses",
        icon: FileText,
        description: "Spend tracking",
    },
];

const assetItems: NavItem[] = [
    {
        name: "Products",
        href: "/dashboard/assets/products",
        icon: Archive,
        description: "Catalog",
    },
    {
        name: "Services",
        href: "/dashboard/assets/services",
        icon: Workflow,
        description: "Service lines",
    },
    {
        name: "Assets",
        href: "/dashboard/assets/assets",
        icon: FolderKanban,
        description: "Inventory",
    },
    {
        name: "Liability",
        href: "/dashboard/assets/liability",
        icon: Wallet,
        description: "Coverage",
    },
    {
        name: "Contracts",
        href: "/dashboard/assets/contracts",
        icon: FileText,
        description: "Agreements",
    },
];

const peopleItems: NavItem[] = [
    {
        name: "Leave Center",
        href: "/dashboard/leave",
        icon: CalendarClock,
        description: "Requests",
    },
    {
        name: "Leave Requests",
        href: "/dashboard/leave/requests",
        icon: FileText,
        description: "Queue",
    },
    {
        name: "Leave Calendar",
        href: "/dashboard/leave/calendar",
        icon: Calendar,
        description: "Schedule",
    },
    {
        name: "Leave Balance",
        href: "/dashboard/leave/balance",
        icon: Wallet,
        description: "Accruals",
    },
    {
        name: "Approvals",
        href: "/dashboard/leave/approvals",
        icon: ShieldCheck,
        description: "Manager view",
    },
    {
        name: "Policies",
        href: "/dashboard/leave/policies",
        icon: NotebookPen,
        description: "Rules",
    },
];

const knowledgeItems: NavItem[] = [
    {
        name: "Organization Files",
        href: "/organization/files",
        icon: FileText,
        description: "Shared docs",
    },
    {
        name: "Notes",
        href: "/organization/notes",
        icon: NotebookPen,
        description: "Meeting notes",
    },
    {
        name: "Tables",
        href: "/organization/tables",
        icon: Database,
        description: "Structured data",
    },
    {
        name: "Personal Files",
        href: "/personal/files",
        icon: FileText,
        description: "Private docs",
    },
    {
        name: "Personal Notes",
        href: "/personal/notes",
        icon: NotebookPen,
        description: "Quick captures",
    },
];

const sections = [
    { title: "Core", items: primaryItems },
    { title: "Growth", items: growthItems },
    { title: "Operations", items: operationsItems },
    { title: "Finance", items: financeItems },
    { title: "Assets", items: assetItems },
    { title: "People", items: peopleItems },
    { title: "Knowledge", items: knowledgeItems },
];

export default function Sidebar() {
    const pathname = usePathname();
    const [activeSection, setActiveSection] = useState("Core");
    const [openSection, setOpenSection] = useState<string | null>("Core");
    const [isMobileOpen, setIsMobileOpen] = useState(false);
    const isCommandCenterActive = pathname === "/dashboard";

    const isActiveRoute = useCallback((item: NavItem) => {
        if (item.match === "prefix") {
            return pathname.startsWith(item.href);
        }
        return pathname === item.href;
    }, [pathname]);

    useEffect(() => {
        const matchingSection = sections.find((section) =>
            section.items.some((item) => isActiveRoute(item))
        );
        if (matchingSection) {
            setActiveSection(matchingSection.title);
            setOpenSection(matchingSection.title);
        }
    }, [pathname, isActiveRoute]);

    const handleNavItemClick = useCallback(() => {
        setIsMobileOpen(false);
    }, []);

    const commandCenterLink = (
        <Link
            href="/dashboard"
            title="Command Center"
            onClick={handleNavItemClick}
            className={`group flex items-center gap-3 rounded-2xl border px-3 py-2 text-xs transition-all duration-200 lg:px-4 lg:text-sm ${
                isCommandCenterActive
                    ? "border-slate-900 bg-slate-900 text-white shadow-[0_18px_40px_-30px_rgba(15,23,42,0.8)]"
                    : "border-slate-200/70 bg-white/80 text-slate-600 hover:border-slate-300 hover:bg-white"
            }`}
        >
            <span
                className={`flex h-9 w-9 items-center justify-center rounded-xl border ${
                    isCommandCenterActive
                        ? "border-white/20 bg-white/10"
                        : "border-slate-200/70 bg-slate-50"
                }`}
            >
                <LayoutDashboard
                    className={`h-4 w-4 ${
                        isCommandCenterActive ? "text-white" : "text-slate-500"
                    }`}
                />
            </span>
            <span className="flex-1">
                <span className="block font-medium">Command Center</span>
                <span
                    className={`hidden text-xs lg:block ${
                        isCommandCenterActive ? "text-white/70" : "text-slate-400"
                    }`}
                >
                    Always within reach
                </span>
            </span>
        </Link>
    );

    const navSections = (
        <div className="space-y-3">
            {sections.map((section) => {
                const isOpen = openSection === section.title;

                return (
                    <div key={section.title} className="rounded-2xl border border-slate-200/70 bg-white/80 p-3">
                        <button
                            type="button"
                            onClick={() => {
                                setActiveSection(section.title);
                                setOpenSection((prev) => (prev === section.title ? null : section.title));
                            }}
                            aria-expanded={isOpen}
                            className="flex w-full items-center justify-between text-left"
                        >
                            <div>
                                <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-slate-400">
                                    {section.title}
                                </p>
                                <p className="text-xs text-slate-500">{section.items.length} destinations</p>
                            </div>
                            <span className="flex items-center gap-2 rounded-full border border-slate-200/70 bg-white px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                                View
                                <ChevronDown
                                    className={`h-3.5 w-3.5 transition-transform ${
                                        isOpen ? "rotate-180" : "rotate-0"
                                    }`}
                                />
                            </span>
                        </button>
                        <div className={`${isOpen ? "mt-3 space-y-2" : "hidden"}`}>
                            {section.items.map((item) => {
                                const isActive = isActiveRoute(item);

                                return (
                                    <Link
                                        key={item.name}
                                        href={item.href}
                                        title={item.name}
                                        onClick={handleNavItemClick}
                                        className={`group flex items-center gap-3 rounded-2xl border px-3 py-2 text-xs transition-all duration-200 lg:text-sm ${
                                            isActive
                                                ? "border-slate-900 bg-slate-900 text-white shadow-[0_18px_40px_-30px_rgba(15,23,42,0.8)]"
                                                : "border-slate-200/70 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                                        }`}
                                    >
                                        <span
                                            className={`flex h-9 w-9 items-center justify-center rounded-xl border ${
                                                isActive
                                                    ? "border-white/20 bg-white/10"
                                                    : "border-slate-200/70 bg-slate-50"
                                            }`}
                                        >
                                            <item.icon
                                                className={`h-4 w-4 ${
                                                    isActive ? "text-white" : "text-slate-500"
                                                }`}
                                            />
                                        </span>
                                        <span className="flex-1">
                                            <span className="block font-medium">{item.name}</span>
                                            {item.description && (
                                                <span
                                                    className={`hidden text-xs xl:block ${
                                                        isActive ? "text-white/70" : "text-slate-400"
                                                    }`}
                                                >
                                                    {item.description}
                                                </span>
                                            )}
                                        </span>
                                        {item.badge && (
                                            <span
                                                className={`hidden rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] lg:inline-flex ${
                                                    isActive ? "bg-white/15 text-white" : "bg-slate-900 text-white"
                                                }`}
                                            >
                                                {item.badge}
                                            </span>
                                        )}
                                    </Link>
                                );
                            })}
                        </div>
                    </div>
                );
            })}
        </div>
    );

    return (
        <>
            <div className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/95 px-4 py-3 backdrop-blur lg:hidden">
                <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200/70 bg-white">
                            <Image src="/logo.png" alt="Carlhub" width={22} height={22} />
                        </div>
                        <div>
                            <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-400">Carlhub</p>
                            <p className="text-sm font-semibold text-slate-700">Dashboard</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link
                            href="/dashboard"
                            onClick={handleNavItemClick}
                            className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] ${
                                isCommandCenterActive
                                    ? "border-slate-900 bg-slate-900 text-white"
                                    : "border-slate-200/70 bg-white text-slate-500"
                            }`}
                        >
                            <LayoutDashboard className="h-3.5 w-3.5" />
                            Command
                        </Link>
                        <button
                            type="button"
                            onClick={() => setIsMobileOpen((prev) => !prev)}
                            aria-controls="sidebar-menu"
                            aria-expanded={isMobileOpen}
                            className="inline-flex items-center gap-2 rounded-full border border-slate-200/70 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500"
                        >
                            {isMobileOpen ? <X className="h-3.5 w-3.5" /> : <Menu className="h-3.5 w-3.5" />}
                            {isMobileOpen ? "Close" : "Menu"}
                        </button>
                    </div>
                </div>
            </div>

            <div className={`fixed inset-0 z-40 lg:hidden ${isMobileOpen ? "" : "pointer-events-none"}`}>
                <div
                    className={`absolute inset-0 bg-slate-950/40 transition-opacity ${
                        isMobileOpen ? "opacity-100" : "opacity-0"
                    }`}
                    onClick={() => setIsMobileOpen(false)}
                />
                <aside
                    id="sidebar-menu"
                    className={`absolute left-0 top-0 flex h-full w-[86%] max-w-sm flex-col gap-5 border-r border-slate-200/70 bg-white/95 px-4 py-5 shadow-[0_24px_60px_-30px_rgba(15,23,42,0.6)] transition-transform ${
                        isMobileOpen ? "translate-x-0" : "-translate-x-full"
                    }`}
                >
                    <div className="rounded-[26px] border border-slate-200/70 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.12),_transparent_60%),linear-gradient(135deg,_rgba(241,245,249,0.95),_rgba(255,255,255,0.9))] p-4 text-slate-700 shadow-[0_18px_45px_-30px_rgba(15,23,42,0.3)]">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/60 bg-white">
                                    <Image src="/logo.png" alt="Carlhub" width={26} height={26} />
                                </div>
                                <div>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-slate-400">
                                        Workspace
                                    </p>
                                    <p className="font-display text-lg font-semibold">Carlhub HQ</p>
                                </div>
                            </div>
                            <span className="rounded-full border border-slate-200/70 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500">
                                Prime
                            </span>
                        </div>
                        <div className="mt-4 flex items-center justify-between rounded-2xl border border-white/80 bg-white/60 px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-400">
                            <span>Pulse</span>
                            <span className="text-slate-700">+8.2%</span>
                        </div>
                    </div>

                    {commandCenterLink}

                    <nav className="flex-1 overflow-y-auto pb-4">
                        {navSections}
                    </nav>

                    <div className="flex items-center justify-between rounded-[22px] border border-slate-200/70 bg-white/80 px-4 py-3 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500">
                        <span className="flex items-center gap-2">
                            <LifeBuoy className="h-4 w-4" />
                            Support
                        </span>
                        <span className="text-[10px] text-slate-400">24/7</span>
                    </div>
                </aside>
            </div>

            <aside className="hidden w-full border-r border-slate-200/70 bg-white/90 backdrop-blur lg:sticky lg:top-0 lg:flex lg:h-screen">
                <div className="flex h-full w-full flex-col gap-5 px-6 py-6">
                    <div className="rounded-[26px] border border-slate-200/70 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.12),_transparent_60%),linear-gradient(135deg,_rgba(241,245,249,0.95),_rgba(255,255,255,0.9))] p-4 text-slate-700 shadow-[0_18px_45px_-30px_rgba(15,23,42,0.3)]">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/60 bg-white">
                                    <Image src="/logo.png" alt="Carlhub" width={26} height={26} />
                                </div>
                                <div>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-slate-400">
                                        Workspace
                                    </p>
                                    <p className="font-display text-lg font-semibold">Carlhub HQ</p>
                                </div>
                            </div>
                            <span className="rounded-full border border-slate-200/70 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500">
                                Prime
                            </span>
                        </div>
                        <div className="mt-4 flex items-center justify-between rounded-2xl border border-white/80 bg-white/60 px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-400">
                            <span>Pulse</span>
                            <span className="text-slate-700">+8.2%</span>
                        </div>
                    </div>

                    {commandCenterLink}

                    <nav className="flex-1 overflow-y-auto pb-4">
                        {navSections}
                    </nav>

                    <div className="flex items-center justify-between rounded-[22px] border border-slate-200/70 bg-white/80 px-4 py-3 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500 lg:text-xs">
                        <span className="flex items-center gap-2">
                            <LifeBuoy className="h-4 w-4" />
                            Support
                        </span>
                        <span className="text-[10px] text-slate-400">24/7</span>
                    </div>
                </div>
            </aside>
        </>
    );
}
