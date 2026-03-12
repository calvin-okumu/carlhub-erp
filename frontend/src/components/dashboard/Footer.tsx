import React from 'react';
import Link from 'next/link';

export default function Footer() {
    return (
        <footer className="border-t border-slate-200/70 bg-white/80">
            <div className="mx-auto flex max-w-[1440px] flex-col items-center gap-2 px-4 py-6 text-sm text-slate-500 sm:flex-row sm:justify-between sm:px-6 lg:px-10">
                <p>© 2025 Carlhub. All systems operational.</p>
                <div className="flex items-center gap-4 text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">
                    <Link href="#" className="transition hover:text-slate-600">
                        Privacy
                    </Link>
                    <Link href="#" className="transition hover:text-slate-600">
                        Status
                    </Link>
                </div>
            </div>
        </footer>
    );
}
