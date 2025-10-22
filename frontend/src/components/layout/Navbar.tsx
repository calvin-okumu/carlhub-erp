"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Bell, Menu, Search, User, LogOut, Building, Users } from "lucide-react";

export default function Header() {
    const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
    const router = useRouter();
    const dropdownRef = useRef<HTMLDivElement>(null);

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

    return (
        <header className="bg-white shadow-lg border-b border-gray-200">
            <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Center: Search bar */}
                    <div className="hidden md:flex flex-1 justify-center px-6">
                        <div className="w-full max-w-lg">
                            <label htmlFor="search" className="sr-only">
                                Search
                            </label>
                            <div className="relative">
                                <Search
                                    className="absolute top-1/2 -translate-y-1/2 left-3 h-5 w-5 text-gray-400"
                                    aria-hidden="true"
                                />
                                <input
                                    id="search"
                                    name="search"
                                    type="search"
                                    placeholder="Search apps..."
                                    className="block w-full pl-10 pr-4 py-2 rounded-md border border-gray-300 text-sm bg-gray-50 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex items-center space-x-4">
                        {/* Notifications */}
                        <button
                            type="button"
                            className="p-2 rounded-full text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <span className="sr-only">View notifications</span>
                            <Bell className="h-6 w-6" aria-hidden="true" />
                        </button>

                        {/* Profile */}
                        <div className="relative" ref={dropdownRef}>
                            <button
                                type="button"
                                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                                className="flex items-center justify-center h-9 w-9 rounded-full bg-blue-100 text-blue-600 hover:ring-2 hover:ring-blue-500 focus:outline-none"
                            >
                                <span className="sr-only">Open user menu</span>
                                <User className="h-5 w-5" />
                            </button>
                            {isProfileMenuOpen && (
                                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10">
                                    <div className="py-1">
                                        <a
                                            href="/dashboard/user-management/profile"
                                            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        >
                                            <User className="mr-3 h-4 w-4" />
                                            Profile
                                        </a>
                                        <a
                                            href="/organizations"
                                            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        >
                                            <Building className="mr-3 h-4 w-4" />
                                            Organization List
                                        </a>
                                        <a
                                            href="/user-management"
                                            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        >
                                            <Users className="mr-3 h-4 w-4" />
                                            User Management
                                        </a>
                                        <div className="border-t border-gray-100"></div>
                                        <button
                                            onClick={() => {
                                                localStorage.removeItem("access_token");
                                                localStorage.removeItem("refresh_token");
                                                localStorage.removeItem("user");
                                                setIsProfileMenuOpen(false);
                                                router.push("/login");
                                            }}
                                            className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                        >
                                            <LogOut className="mr-3 h-4 w-4" />
                                            Logout
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Mobile menu button (hidden on desktop) */}
                        <button
                            type="button"
                            className="md:hidden p-2 rounded-md text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <span className="sr-only">Open menu</span>
                            <Menu className="h-6 w-6" />
                        </button>
                    </div>
                </div>

                {/* Mobile Search (visible only on small screens) */}
                <div className="flex md:hidden mt-2">
                    <div className="w-full">
                        <div className="relative">
                            <Search
                                className="absolute top-1/2 -translate-y-1/2 left-3 h-5 w-5 text-gray-400"
                                aria-hidden="true"
                            />
                            <input
                                id="mobile-search"
                                type="search"
                                placeholder="Search apps..."
                                className="block w-full pl-10 pr-3 py-2 rounded-md border border-gray-300 text-sm bg-gray-50 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
