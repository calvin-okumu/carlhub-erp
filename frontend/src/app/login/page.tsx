"use client";

import { fetchMe, login, refreshAccessToken } from "@/api/auth";
import AuthLayout from "@/components/AuthLayout";
import { AlertCircle, CheckCircle2, Eye, EyeOff } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

type FormData = {
    email: string;
    password: string;
};

export default function LoginPage() {
    const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);
    const [checkingSession, setCheckingSession] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const bootstrapAuth = async () => {
            const token = localStorage.getItem("access_token");
            if (token) {
                router.replace("/dashboard");
                return;
            }

            const refreshed = await refreshAccessToken();
            if (refreshed) {
                router.replace("/dashboard");
                return;
            }

            setCheckingSession(false);
        };

        bootstrapAuth();
    }, [router]);

    const onSubmit = async (data: FormData) => {
        setError("");
        setSuccess("");
        setLoading(true);

        try {
            const result = await login(data.email, data.password);

            // Store access token first so fetchMe can use it
            localStorage.setItem("access_token", result.access);

            // Fetch RBAC context (role, is_owner, tenant etc.) from /api/me/
            const me = await fetchMe(result.access);

            localStorage.setItem("user", JSON.stringify({
                id:          result.user_id,
                email:       result.email,
                first_name:  result.first_name,
                last_name:   result.last_name,
                // RBAC fields — populated from /api/me/ response
                role:        me?.role        ?? 'Employee',
                is_owner:    me?.is_owner    ?? false,
                is_approved: me?.is_approved ?? false,
                tenant:      me?.tenant      ?? null,
                tenant_name: me?.tenant_name ?? null,
                department:  me?.department  ?? null,
            }));

            setSuccess("Login successful! Redirecting...");
            setTimeout(() => router.push("/dashboard"), 5);
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError("Login failed. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };



    if (checkingSession) {
        return null;
    }

    return (
        <AuthLayout>
            <div>
                <div className="text-center">
                    <p className="text-xs font-semibold uppercase tracking-[0.32em] text-slate-400">Sign in</p>
                    <h2 className="font-display mt-3 text-3xl font-semibold text-slate-900">Welcome back</h2>
                    <p className="mt-2 text-sm text-slate-600">Access your workspace and continue where you left off.</p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
                    {/* Email */}
                    <div>
                        <label htmlFor="email" className="block text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Email</label>
                        <input
                            id="email"
                            type="email"
                            placeholder="Enter your email"
                            className="mt-2 w-full rounded-2xl border border-slate-200/70 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm transition-colors focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
                            {...register("email", { required: "Email is required", pattern: { value: /^\S+@\S+$/i, message: "Invalid email address" } })}
                        />
                        {errors.email && <p className="mt-2 text-xs text-rose-500">{errors.email.message}</p>}
                    </div>

                    {/* Password */}
                    <div>
                        <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Password</label>
                        <div className="relative">
                            <input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="Enter your password"
                                className="mt-2 w-full rounded-2xl border border-slate-200/70 bg-white px-4 py-3 pr-12 text-sm text-slate-700 shadow-sm transition-colors focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
                                {...register("password", { required: "Password is required" })}
                            />
                            {errors.password && <p className="mt-2 text-xs text-rose-500">{errors.password.message}</p>}
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600"
                                aria-label={showPassword ? "Hide password" : "Show password"}
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                    </div>

                    {/* Alerts */}
                    {error && (
                        <div className="flex items-center gap-3 rounded-2xl border border-rose-200/70 bg-rose-50/80 p-4 text-rose-800">
                            <AlertCircle size={20} />
                            <span className="text-sm">{error}</span>
                        </div>
                    )}
                    {success && (
                        <div className="flex items-center gap-3 rounded-2xl border border-emerald-200/70 bg-emerald-50/80 p-4 text-emerald-800">
                            <CheckCircle2 size={20} />
                            <span className="text-sm">{success}</span>
                        </div>
                    )}

                    <button
                        type="submit"
                        className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white shadow-lg shadow-slate-900/20 transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                        disabled={loading}
                    >
                        {loading ? (
                            <div className="flex items-center justify-center">
                                <div className="mr-2 h-5 w-5 animate-spin rounded-full border-b-2 border-white"></div>
                                Signing in...
                            </div>
                        ) : (
                            "Sign in"
                        )}
                    </button>
                </form>

                <div className="mt-8">
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-slate-200/70" />
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="bg-white px-4 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Or continue with</span>
                        </div>
                    </div>
                    <div className="mt-6 grid grid-cols-2 gap-4">
                        <button
                            onClick={() => window.location.href = 'http://127.0.0.1:8000/accounts/google/login/'}
                            className="inline-flex w-full items-center justify-center gap-3 rounded-2xl border border-slate-200/70 bg-white px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-white"
                        >
                            <svg className="w-5 h-5 text-red-500" viewBox="0 0 24 24">
                                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                            </svg>
                            <span className="ml-3">Google</span>
                        </button>
                        <button
                            onClick={() => window.location.href = 'http://127.0.0.1:8000/accounts/github/login/'}
                            className="inline-flex w-full items-center justify-center gap-3 rounded-2xl border border-slate-200/70 bg-white px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-white"
                        >
                            <svg className="w-5 h-5 text-gray-900" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                            </svg>
                            <span className="ml-3">GitHub</span>
                        </button>
                    </div>
                </div>

                <p className="mt-8 text-center text-sm text-slate-600">
                    New here?{" "}
                    <a href="/signup" className="font-semibold text-slate-900 transition-colors hover:text-slate-700">
                        Create an account
                    </a>
                </p>
            </div>
        </AuthLayout>
    );
}
