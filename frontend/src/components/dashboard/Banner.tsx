
"use client";

// Logo is now used from /logo.png
import Image from "next/image";
import { useEffect, useState } from "react";

export default function Banner() {
    const [firstName, setFirstName] = useState("User");

    useEffect(() => {
        const user = localStorage.getItem("user");
        if (user) {
            const parsed = JSON.parse(user);
            const name = parsed.first_name || (parsed.email ? parsed.email.split('@')[0] : "User");
            setFirstName(name);
        }
    }, []);
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="group bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl shadow-lg p-8 text-white transition-all duration-300 hover:shadow-xl">
                <div className="flex items-center space-x-4">
                    {/* Logo/Icon */}
                    <div className="bg-white/20 p-3 rounded-xl ring-1 ring-white/30">
                        <Image src="/logo.png" alt="CarlHub Logo" width={32} height={32} className="h-8 w-8 transition-transform duration-300 ease-in-out
     group-hover:rotate-12" />
                    </div>

                    {/* Text */}
                    <div>
                        <h1 className="text-2xl font-bold">Welcome back, {firstName}!</h1>
                        <p className="text-blue-100">
                            Manage your business with AI-powered tools. Choose a service below to get started.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
