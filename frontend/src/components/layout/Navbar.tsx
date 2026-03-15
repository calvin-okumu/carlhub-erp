"use client";

import {
    Bell,
    Building,
    ChevronDown,
    LogOut,
    Plus,
    Search,
    User,
    Users,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { logout } from "@/api";
import { useEffect, useRef, useState } from "react";
import { useAuth, clearSession } from "@/hooks/useAuth";
import { isSeniorOrAbove } from "@/utils/permissions";

export default function Header() {
    const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const router = useRouter();
    const dropdownRef = useRef<HTMLDivElement>(null);
    const { user, role, isOwner } = useAuth();

    // Derive display values from the session
    const displayName = user.first_name
        ? `${user.first_name} ${user.last_name}`.trim()
        : user.email || 'User';
    const initials = user.first_name
        ? `${user.first_name[0]}${user.last_name?.[0] ?? ''}`.toUpperCase()
        : 'U';
    // User Management link is visible to General Manager and above, or the owner
    const canManageUsers = isOwner || isSeniorOrAbove(role);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsProfileMenuOpen(false);
            }
        }

        if (isProfileMenuOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isProfileMenuOpen]);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            // Only perform search navigation if we're on the main dashboard page
            if (window.location.pathname === '/dashboard') {
                if (searchQuery.trim()) {
                    router.push(`/dashboard?search=${encodeURIComponent(searchQuery)}`);
                } else {
                    router.push('/dashboard');
                }
            }
            // On other pages, don't navigate - search functionality is disabled
        }, 300); // Debounce

        return () => clearTimeout(timeoutId);
    }, [searchQuery, router]);

    return (
        <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/80 backdrop-blur">
            <div className="mx-auto max-w-[1480px] px-4 sm:px-6 lg:px-10">
                <div className="flex flex-col gap-4 py-5 md:flex-row md:items-center md:justify-between">
                    <div className="space-y-1">
                        <p className="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">
                            Control Deck
                        </p>
                        <div className="flex flex-wrap items-center gap-3">
                            <h1 className="font-display text-2xl font-semibold text-slate-900">
                                Command Center
                            </h1>
                            <span className="rounded-full border border-slate-200/70 bg-white px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-slate-500">
                                Shift 12
                            </span>
                            <span className="rounded-full border border-emerald-200/70 bg-emerald-50 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.25em] text-emerald-700">
                                Live
                            </span>
                        </div>
                    </div>

                    <div className="flex flex-1 items-center gap-3 md:max-w-xl md:justify-center">
                        <label htmlFor="search" className="sr-only">
                            Search
                        </label>
                        <div className="relative w-full">
                            <Search
                                className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                                aria-hidden="true"
                            />
                            <input
                                id="search"
                                name="search"
                                type="search"
                                placeholder="Search workflows, teams, or records"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="block w-full rounded-[26px] border border-slate-200/70 bg-slate-50/80 py-3 pl-11 pr-4 text-sm text-slate-700 placeholder-slate-400 shadow-[0_12px_30px_-24px_rgba(15,23,42,0.5)] focus:border-slate-300 focus:outline-none"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            className="hidden items-center gap-2 rounded-full border border-slate-200/70 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-slate-600 transition hover:border-slate-300 hover:text-slate-900 md:inline-flex"
                        >
                            <Plus className="h-4 w-4" />
                            New
                        </button>

                        <button
                            type="button"
                            className="relative rounded-full border border-slate-200/70 bg-white/80 p-2 text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
                        >
                            <span className="sr-only">View notifications</span>
                            <Bell className="h-5 w-5" aria-hidden="true" />
                            <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-rose-500" />
                        </button>

                        <div className="relative" ref={dropdownRef}>
                            <button
                                type="button"
                                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                                className="flex items-center gap-2 rounded-full border border-slate-200/70 bg-white/80 px-2 py-1.5 text-sm text-slate-600 hover:border-slate-300"
                                title={`${displayName} — ${role}`}
                            >
                                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-white text-xs font-bold">
                                    {initials}
                                </span>
                                <span className="hidden flex-col items-start md:flex">
                                    <span className="text-xs font-semibold text-slate-700 leading-tight max-w-[100px] truncate">
                                        {displayName}
                                    </span>
                                    <span className="text-[10px] uppercase tracking-[0.18em] text-slate-400 leading-tight">
                                        {role}
                                    </span>
                                </span>
                                <ChevronDown className="h-4 w-4 text-slate-400" />
                            </button>
                            {isProfileMenuOpen && (
                                <div className="absolute right-0 mt-2 w-60 rounded-2xl border border-slate-200/70 bg-white shadow-xl">
                                    {/* User identity header */}
                                    <div className="px-4 py-3 border-b border-slate-100">
                                        <p className="text-sm font-semibold text-slate-800 truncate">{displayName}</p>
                                        <p className="text-xs text-slate-400 truncate">{user.email}</p>
                                        <span className="mt-1.5 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                                            {role}
                                        </span>
                                    </div>
                                    <div className="p-2">
                                        <button
                                            onClick={() => {
                                                setIsProfileMenuOpen(false);
                                                router.push("/dashboard/user-management/profile");
                                            }}
                                            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                                        >
                                            <User className="h-4 w-4" />
                                            Profile
                                        </button>
                                        <button
                                            onClick={() => {
                                                setIsProfileMenuOpen(false);
                                                router.push("/organizations");
                                            }}
                                            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                                        >
                                            <Building className="h-4 w-4" />
                                            Organization List
                                        </button>
                                        {/* User Management — only visible to General Manager and above */}
                                        {canManageUsers && (
                                            <button
                                                onClick={() => {
                                                    setIsProfileMenuOpen(false);
                                                    router.push("/dashboard/user-management/user-management");
                                                }}
                                                className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                                            >
                                                <Users className="h-4 w-4" />
                                                User Management
                                            </button>
                                        )}
                                        <div className="my-2 border-t border-slate-100" />
                                        <button
                                            onClick={async () => {
                                                await logout();
                                                clearSession();
                                                setIsProfileMenuOpen(false);
                                                router.push("/login");
                                            }}
                                            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-rose-600 hover:bg-rose-50"
                                        >
                                            <LogOut className="h-4 w-4" />
                                            Logout
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
