import Image from "next/image";
import Link from "next/link";

export default function Hero() {
    return (
        <section className="relative bg-gradient-to-b from-gray-50 to-white flex items-center justify-center px-6 py-16 md:py-24">
            <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                {/* Left: Text */}
                <div className="text-center md:text-left space-y-6">
                    <span className="text-sm font-semibold text-blue-600 uppercase tracking-wide">
                        Powered by AI
                    </span>
                    <h1 className="text-4xl md:text-5xl font-extrabold leading-tight">
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                            Intelligent
                        </span>{" "}
                        Business Management
                    </h1>
                    <p className="text-gray-600 text-lg max-w-xl mx-auto md:mx-0">
                        Streamline operations, empower your team, and grow faster with
                        Carlhub’s AI-driven business tools.
                    </p>
                    <div className="flex flex-col sm:flex-row sm:justify-start sm:space-x-4 space-y-4 sm:space-y-0">
                        <Link
                            href="/signup"
                            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium shadow-md"
                        >
                            Get Started
                        </Link>
                        <Link
                            href="/login"
                            className="border border-blue-500 text-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50 transition font-medium"
                        >
                            Sign In
                        </Link>
                    </div>
                </div>

                {/* Right: Image */}
                <div className="flex justify-center md:justify-end">
                    <div className="relative">
                        <Image
                            src="/hero.png"
                            alt="Business management illustration"
                            width={520}
                            height={420}
                            className="rounded-xl shadow-lg"
                            priority
                        />
                        {/* Decorative background shape */}
                        <div className="absolute -top-6 -left-6 w-24 h-24 bg-blue-100 rounded-full blur-3xl opacity-50"></div>
                    </div>
                </div>
            </div>
        </section>
    );
}
