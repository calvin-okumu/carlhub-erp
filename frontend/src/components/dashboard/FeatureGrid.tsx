
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

const features = [
    {
        title: "Contact Management",
        subtitle: "Organize and manage all your contacts",
        icon: Users,
        color: "bg-green-400",
        hoverColor: "hover:shadow-green-400/20 hover:border-green-400 hover:bg-green-400/10",
        buttonColor: "bg-gradient-to-r from-green-400 to-green-500 hover:from-green-500 hover:to-green-600",
        cta: "View Contacts",
        href: "/dashboard/contacts/contact-list",
        active: true,
    },
    {
        title: "Customer Relations CRM",
        subtitle: "Build stronger customer relationships",
        icon: UserCheck,
        color: "bg-orange-400",
        hoverColor: "hover:shadow-orange-400/20 hover:border-orange-400 hover:bg-orange-400/10",
        buttonColor: "bg-gradient-to-r from-orange-400 to-orange-500 hover:from-orange-500 hover:to-orange-600",
        cta: "View CRM",
        href: "/dashboard/crm/clients",
        active: true,
    },
    {
        title: "Vendor Management",
        subtitle: "Manage suppliers and vendors efficiently",
        icon: Building,
        color: "bg-blue-400",
        hoverColor: "hover:shadow-blue-400/20 hover:border-blue-400 hover:bg-blue-400/10",
        buttonColor: "bg-gradient-to-r from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600",
        cta: "View Vendors",
        href: "/dashboard/vendors/vendor-list",
        active: true,
    },
    {
        title: "Financial Management",
        subtitle: "Handle finances and accounting",
        icon: DollarSign,
        color: "bg-red-400",
        hoverColor: "hover:shadow-red-400/20 hover:border-red-400 hover:bg-red-400/10",
        buttonColor: "bg-gradient-to-r from-red-400 to-red-500 hover:from-red-500 hover:to-red-600",
        cta: "View Finance",
        href: "/dashboard/finance/accounts",
        active: true,
    },
    {
        title: "Asset Management",
        subtitle: "Track and manage company assets",
        icon: Archive,
        color: "bg-gray-500",
        hoverColor: "hover:shadow-gray-500/20 hover:border-gray-500 hover:bg-gray-500/10",
        buttonColor: "bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700",
        cta: "View Assets",
        href: "/dashboard/assets/products",
        active: true,
    },
    {
        title: "Project Management",
        subtitle: "Plan and track project progress",
        icon: FolderOpen,
        color: "bg-yellow-400",
        hoverColor: "hover:shadow-yellow-400/20 hover:border-yellow-400 hover:bg-yellow-400/10",
        buttonColor: "bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600",
        cta: "View Projects",
        href: "/dashboard/project-management/",
        active: true,
    },
    {
        title: "Business Intelligence",
        subtitle: "Advanced analytics and insights",
        icon: TrendingUp,
        color: "bg-purple-400",
        hoverColor: "hover:shadow-purple-400/20 hover:border-purple-400 hover:bg-purple-400/10",
        buttonColor: "",
        cta: "Coming Soon",
        href: "#",
        active: false,
    },
    {
        title: "Reports & Analytics",
        subtitle: "Generate reports and visualize data",
        icon: BarChart3,
        color: "bg-pink-400",
        hoverColor: "hover:shadow-pink-400/20 hover:border-pink-400 hover:bg-pink-400/10",
        buttonColor: "",
        cta: "Coming Soon",
        href: "#",
        active: false,
    },
    {
        title: "Leave Management",
        subtitle: "Manage employee leave and absences",
        icon: Calendar,
        color: "bg-indigo-400",
        hoverColor: "hover:shadow-indigo-400/20 hover:border-indigo-400 hover:bg-indigo-400/10",
        buttonColor: "bg-gradient-to-r from-indigo-400 to-indigo-500 hover:from-indigo-500 hover:to-indigo-600",
        cta: "View Leave",
        href: "/dashboard/leave/leave-requests",
        active: true,
    },
];

export default function FeatureGrid() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-8">
                {features.map((feature) => (
                    <div
                        key={feature.title}
                        className={`bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-gray-100 ${feature.hoverColor}`}
                    >
                        {/* Icon */}
                        <div
                            className={`w-14 h-14 rounded-xl ${feature.color} flex items-center justify-center mb-4 shadow-md`}
                        >
                            <feature.icon className="h-7 w-7 text-white" />
                        </div>

                        {/* Title + Subtitle */}
                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                            {feature.title}
                        </h3>
                        <p className="text-gray-600 mb-6 leading-relaxed">{feature.subtitle}</p>

                        {/* CTA */}
                        {feature.active ? (
                            <Link
                                href={feature.href}
                                className={`block w-full text-center py-3 px-4 rounded-lg font-semibold text-white shadow-md hover:shadow-lg transition-all ${feature.buttonColor}`}
                            >
                                {feature.cta}
                            </Link>
                        ) : (
                            <button
                                disabled
                                aria-disabled="true"
                                className="w-full py-3 px-4 rounded-lg font-semibold bg-gray-100 text-gray-400 cursor-not-allowed"
                            >
                                {feature.cta}
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
