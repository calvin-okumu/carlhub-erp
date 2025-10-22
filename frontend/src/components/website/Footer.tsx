
import { Facebook, Linkedin, Mail, Twitter } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

export default function Footer() {
    return (
        <footer className="bg-gray-900 text-gray-300 shadow-lg">
            <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-4 gap-10">
                {/* Brand */}
                <div>
                    <div className="flex items-center space-x-2 mb-4">
                        <Image
                            src="/logo.png"
                            alt="Carlhub Logo"
                            width={32}
                            height={32}
                            className="rounded-md"
                        />
                        <span className="text-xl font-semibold text-white">Carlhub</span>
                    </div>
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Intelligent business management software to streamline operations,
                        manage your team, and grow with confidence.
                    </p>
                </div>

                {/* Navigation */}
                <div>
                    <h5 className="text-white font-semibold mb-4">Company</h5>
                    <ul className="space-y-2 text-sm">
                        {["Platform", "Features", "Pricing", "Blog", "Careers"].map((item) => (
                            <li key={item}>
                                <Link href={`/${item.toLowerCase()}`} className="hover:text-indigo-400 transition">
                                    {item}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Resources */}
                <div>
                    <h5 className="text-white font-semibold mb-4">Resources</h5>
                    <ul className="space-y-2 text-sm">
                        {["Privacy Policy", "Terms of Service", "Support", "Documentation"].map((item, idx) => (
                            <li key={idx}>
                                <Link href={`/${item.toLowerCase().replace(/\s+/g, "")}`} className="hover:text-indigo-400 transition">
                                    {item}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Contact */}
                <div>
                    <h5 className="text-white font-semibold mb-4">Get in touch</h5>
                    <p className="text-gray-400 text-sm">651 N Broad St, Delaware, 19707</p>
                    <p className="text-gray-400 text-sm">hello@carlhub.com</p>
                    <p className="text-gray-400 text-sm">+1 (555) 123-4567</p>

                    <div className="flex space-x-3 mt-4">
                        {[
                            { Icon: Facebook, href: "#" },
                            { Icon: Twitter, href: "#" },
                            { Icon: Linkedin, href: "#" },
                            { Icon: Mail, href: "mailto:hello@carlhub.com" },
                        ].map(({ Icon, href }, i) => (
                            <a
                                key={i}
                                href={href}
                                className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-800 hover:bg-indigo-600 transition"
                                aria-label={Icon.name}
                            >
                                <Icon className="w-4 h-4 text-white" />
                            </a>
                        ))}
                    </div>
                </div>
            </div>

            {/* Bottom bar */}
            <div className="border-t border-gray-800 text-sm py-4">
                <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between text-gray-500">
                    <p>© {new Date().getFullYear()} Carlhub. All rights reserved.</p>
                    <div className="flex space-x-4 mt-2 md:mt-0">
                        <Link href="/privacy" className="hover:text-indigo-400">Privacy</Link>
                        <Link href="/terms" className="hover:text-indigo-400">Terms</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
