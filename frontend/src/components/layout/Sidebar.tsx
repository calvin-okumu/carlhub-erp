"use client";

import {
    Archive,
    Building,
    Calendar,
    ChevronDown,
    DollarSign,
    FileText,
    Folder,
    FolderOpen,
    Home,
    MessageCircle,
    StickyNote,
    Table,
    UserCheck,
    Users,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const navigation = [
    { name: "Home", href: "/dashboard", icon: Home },
    { name: "Chat", href: "/chat", icon: MessageCircle },
];

const organizationItems = [
    { name: "Files", href: "/organization/files", icon: FileText },
    { name: "Notes", href: "/organization/notes", icon: StickyNote },
    { name: "Tables", href: "/organization/tables", icon: Table },
];

const personalItems = [
    { name: "My Files", href: "/personal/files", icon: FileText },
    { name: "My Notes", href: "/personal/notes", icon: StickyNote },
];

const crmItems = [
    { name: "Clients", href: "/dashboard/crm/clients", icon: UserCheck },
    { name: "Marketing", href: "/dashboard/crm/marketing", icon: FileText },
    { name: "Campaigns", href: "/dashboard/crm/campaigns", icon: StickyNote },
    { name: "Sales", href: "/dashboard/crm/sales", icon: Table },
    { name: "Sales Funnel", href: "/dashboard/crm/sales-funnel", icon: Building },
];

const projectItems = [
    { name: "Project", href: "/dashboard/project-management", icon: FolderOpen },
];

const contactItems = [
    { name: "Contact List", href: "/dashboard/contacts/contact-list", icon: Users },
    { name: "Contact Group", href: "/dashboard/contacts/contact-group", icon: UserCheck },
];

const vendorItems = [
    { name: "Vendor List", href: "/dashboard/vendors/vendor-list", icon: Building },
];

const financeItems = [
    { name: "Accounts", href: "/dashboard/finance/accounts", icon: DollarSign },
    { name: "Quotes", href: "/dashboard/finance/quotes", icon: FileText },
    { name: "Invoices", href: "/dashboard/finance/invoices", icon: StickyNote },
    { name: "Expenses", href: "/dashboard/finance/expenses", icon: Table },
];

const assetItems = [
    { name: "Products", href: "/dashboard/assets/products", icon: Archive },
    { name: "Services", href: "/dashboard/assets/services", icon: Building },
    { name: "Assets", href: "/dashboard/assets/assets", icon: Folder },
    { name: "Liability", href: "/dashboard/assets/liability", icon: DollarSign },
    { name: "Contracts", href: "/dashboard/assets/contracts", icon: FileText },
];

const leaveItems = [
    { name: "Leave Requests", href: "/dashboard/leave/leave-requests", icon: FileText },
    { name: "Leave Calendar", href: "/dashboard/leave/leave-calendar", icon: Calendar },
    { name: "Leave Balance", href: "/dashboard/leave/leave-balance", icon: DollarSign },
    { name: "Leave Approvals", href: "/dashboard/leave/leave-approvals", icon: UserCheck },
    { name: "Leave Policies", href: "/dashboard/leave/leave-policies", icon: StickyNote },
];

export default function Sidebar() {
    const pathname = usePathname();
    const [isOrgOpen, setIsOrgOpen] = useState(false);
    const [isPersonalOpen, setIsPersonalOpen] = useState(false);

    return (
        <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
            {/* Sidebar container */}
            <div className="flex flex-col flex-1 bg-white border-r border-gray-200 shadow-lg">
                {/* Brand / Logo */}
                <div className="flex items-center h-16 px-4 border-b border-gray-100">
                    <Image
                        src="/logo.png"
                        alt="Carlhub Logo"
                        width={32}
                        height={32}
                        className="mr-2"
                    />
                     <h1 className="text-2xl font-bold text-blue-600">Carlhub</h1>
                 </div>

                 {/* Navigation */}
                <div className="flex-1 overflow-y-auto pt-6">
                    <nav className="px-2 space-y-1">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;

                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`${isActive
                                        ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                        : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                        } group flex items-center px-3 py-2 text-sm font-medium rounded-md`}
                                >
                                    <item.icon
                                        className={`${isActive
                                            ? "text-blue-500"
                                            : "text-gray-400 group-hover:text-gray-500"
                                            } mr-3 h-6 w-6`}
                                    />
                                    {item.name}
                                </Link>
                            );
                        })}

                        {/* Default Organization */}
                        <div>
                            <button
                                onClick={() => setIsOrgOpen(!isOrgOpen)}
                                className="w-full flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md"
                            >
                                <Building className="mr-3 h-6 w-6 text-gray-400" />
                                Default Org.
                                <ChevronDown
                                    className={`ml-auto h-4 w-4 transition-transform ${isOrgOpen ? 'rotate-180' : ''}`}
                                />
                            </button>
                            {isOrgOpen && (
                                <div className="ml-6 mt-1 space-y-1">
                                    {organizationItems.map((item) => (
                                        <Link
                                            key={item.name}
                                            href={item.href}
                                            className="flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md"
                                        >
                                            <item.icon className="mr-3 h-4 w-4 text-gray-400" />
                                            {item.name}
                                        </Link>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Personal Directory */}
                        <div>
                            <button
                                onClick={() => setIsPersonalOpen(!isPersonalOpen)}
                                className="w-full flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md"
                            >
                                <Folder className="mr-3 h-6 w-6 text-gray-400" />
                                Personal Directory
                                <ChevronDown
                                    className={`ml-auto h-4 w-4 transition-transform ${isPersonalOpen ? 'rotate-180' : ''}`}
                                />
                            </button>
                            {isPersonalOpen && (
                                <div className="ml-6 mt-1 space-y-1">
                                    {personalItems.map((item) => (
                                        <Link
                                            key={item.name}
                                            href={item.href}
                                            className="flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md"
                                        >
                                            <item.icon className="mr-3 h-4 w-4 text-gray-400" />
                                            {item.name}
                                        </Link>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* CRM Section */}
                        {pathname.startsWith('/dashboard/crm') && (
                            <div>
                                <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                                    <UserCheck className="mr-3 h-6 w-6 text-gray-400" />
                                    CUSTOMER RELATIONS
                                </div>
                                <div className="ml-6 mt-1 space-y-1">
                                    {crmItems.map((item) => {
                                        const isActive = pathname === item.href;

                                        return (
                                            <Link
                                                key={item.name}
                                                href={item.href}
                                                className={`${isActive
                                                    ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                                    } flex items-center px-3 py-2 text-sm rounded-md`}
                                            >
                                                <item.icon
                                                    className={`${isActive
                                                        ? "text-blue-500"
                                                        : "text-gray-400"
                                                        } mr-3 h-4 w-4`}
                                                />
                                                {item.name}
                                            </Link>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Project Management Section */}
                        {pathname.startsWith('/dashboard/project-management') && (
                            <div>
                                <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                                    <FolderOpen className="mr-3 h-6 w-6 text-gray-400" />
                                    PROJECT MANAGEMENT
                                </div>
                                <div className="ml-6 mt-1 space-y-1">
                                    {projectItems.map((item) => {
                                        const isActive = pathname === item.href;

                                        return (
                                            <Link
                                                key={item.name}
                                                href={item.href}
                                                className={`${isActive
                                                    ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                                    } flex items-center px-3 py-2 text-sm rounded-md`}
                                            >
                                                <item.icon
                                                    className={`${isActive
                                                        ? "text-blue-500"
                                                        : "text-gray-400"
                                                        } mr-3 h-4 w-4`}
                                                />
                                                {item.name}
                                            </Link>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Contact Management Section */}
                        {pathname.startsWith('/dashboard/contacts') && (
                            <div>
                                <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                                    <Users className="mr-3 h-6 w-6 text-gray-400" />
                                    CONTACT MANAGEMENT
                                </div>
                                <div className="ml-6 mt-1 space-y-1">
                                    {contactItems.map((item) => {
                                        const isActive = pathname === item.href;

                                        return (
                                            <Link
                                                key={item.name}
                                                href={item.href}
                                                className={`${isActive
                                                    ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                                    } flex items-center px-3 py-2 text-sm rounded-md`}
                                            >
                                                <item.icon
                                                    className={`${isActive
                                                        ? "text-blue-500"
                                                        : "text-gray-400"
                                                        } mr-3 h-4 w-4`}
                                                />
                                                {item.name}
                                            </Link>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Vendor Management Section */}
                        {pathname.startsWith('/dashboard/vendors') && (
                            <div>
                                <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                                    <Building className="mr-3 h-6 w-6 text-gray-400" />
                                    VENDOR MANAGEMENT
                                </div>
                                <div className="ml-6 mt-1 space-y-1">
                                    {vendorItems.map((item) => {
                                        const isActive = pathname === item.href;

                                        return (
                                            <Link
                                                key={item.name}
                                                href={item.href}
                                                className={`${isActive
                                                    ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                                    } flex items-center px-3 py-2 text-sm rounded-md`}
                                            >
                                                <item.icon
                                                    className={`${isActive
                                                        ? "text-blue-500"
                                                        : "text-gray-400"
                                                        } mr-3 h-4 w-4`}
                                                />
                                                {item.name}
                                            </Link>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Financial Management Section */}
                        {pathname.startsWith('/dashboard/finance') && (
                            <div>
                                <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                                    <DollarSign className="mr-3 h-6 w-6 text-gray-400" />
                                    FINANCIAL MANAGEMENT
                                </div>
                                <div className="ml-6 mt-1 space-y-1">
                                    {financeItems.map((item) => {
                                        const isActive = pathname === item.href;

                                        return (
                                            <Link
                                                key={item.name}
                                                href={item.href}
                                                className={`${isActive
                                                    ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                                    } flex items-center px-3 py-2 text-sm rounded-md`}
                                            >
                                                <item.icon
                                                    className={`${isActive
                                                        ? "text-blue-500"
                                                        : "text-gray-400"
                                                        } mr-3 h-4 w-4`}
                                                />
                                                {item.name}
                                            </Link>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Asset Management Section */}
                        {pathname.startsWith('/dashboard/assets') && (
                            <div>
                                <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                                    <Archive className="mr-3 h-6 w-6 text-gray-400" />
                                    ASSET MANAGEMENT
                                </div>
                                <div className="ml-6 mt-1 space-y-1">
                                    {assetItems.map((item) => {
                                        const isActive = pathname === item.href;

                                        return (
                                            <Link
                                                key={item.name}
                                                href={item.href}
                                                className={`${isActive
                                                    ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                                    } flex items-center px-3 py-2 text-sm rounded-md`}
                                            >
                                                <item.icon
                                                    className={`${isActive
                                                        ? "text-blue-500"
                                                        : "text-gray-400"
                                                        } mr-3 h-4 w-4`}
                                                />
                                                {item.name}
                                            </Link>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Leave Management Section */}
                        {pathname.startsWith('/dashboard/leave') && (
                            <div>
                                <div className="flex items-center px-3 py-2 text-sm font-medium text-gray-600">
                                    <Calendar className="mr-3 h-6 w-6 text-gray-400" />
                                    LEAVE MANAGEMENT
                                </div>
                                <div className="ml-6 mt-1 space-y-1">
                                    {leaveItems.map((item) => {
                                        const isActive = pathname === item.href;

                                        return (
                                            <Link
                                                key={item.name}
                                                href={item.href}
                                                className={`${isActive
                                                    ? "bg-blue-50 border-r-2 border-blue-500 text-blue-700"
                                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                                    } flex items-center px-3 py-2 text-sm rounded-md`}
                                            >
                                                <item.icon
                                                    className={`${isActive
                                                        ? "text-blue-500"
                                                        : "text-gray-400"
                                                        } mr-3 h-4 w-4`}
                                                />
                                                {item.name}
                                            </Link>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </nav>
                </div>


            </div>
        </div>
    );
}

