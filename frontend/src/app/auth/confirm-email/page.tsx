"use client";

import { confirmEmail } from "@/api";
import AuthLayout from "@/components/AuthLayout";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function ConfirmEmailPage() {
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState("");
    const searchParams = useSearchParams();

    useEffect(() => {
        const token = searchParams.get('token');

        if (!token) {
            setStatus('error');
            setMessage("Invalid confirmation link. No token provided.");
            return;
        }

        const confirm = async () => {
            try {
                const result = await confirmEmail(token);
                setStatus('success');
                setMessage(result.message || "Email confirmed successfully!");
            } catch (err: unknown) {
                setStatus('error');
                if (err instanceof Error) {
                    setMessage(err.message);
                } else {
                    setMessage("Failed to confirm email. Please try again.");
                }
            }
        };

        confirm();
    }, [searchParams]);

    return (
        <AuthLayout>
            <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                <div className="text-center">
                    {status === 'loading' && (
                        <>
                            <Loader2 className="mx-auto h-12 w-12 text-blue-600 animate-spin mb-4" />
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Confirming your email&hellip;</h2>
                            <p className="text-gray-600">Please wait while we verify your email address.</p>
                        </>
                    )}

                    {status === 'success' && (
                        <>
                            <CheckCircle2 className="mx-auto h-12 w-12 text-green-600 mb-4" />
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Email confirmed! 🎉</h2>
                            <p className="text-gray-600 mb-6">{message}</p>

                            <div className="space-y-4">
                                <Link
                                    href="/login"
                                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-semibold inline-block text-center"
                                >
                                    Sign In to Your Account
                                </Link>

                                <p className="text-sm text-gray-600">
                                    Don&apos;t have an account yet?{" "}
                                    <Link href="/signup" className="text-blue-600 hover:text-blue-500 font-semibold">
                                        Create one here
                                    </Link>
                                </p>
                            </div>
                        </>
                    )}

                    {status === 'error' && (
                        <>
                            <AlertCircle className="mx-auto h-12 w-12 text-red-600 mb-4" />
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Confirmation failed</h2>
                            <p className="text-gray-600 mb-6">{message}</p>

                            <div className="space-y-4">
                                <Link
                                    href="/login"
                                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-semibold inline-block text-center"
                                >
                                    Go to Login
                                </Link>

                                <p className="text-sm text-gray-600">
                                    Need help?{" "}
                                    <a href="mailto:support@carlhub.com" className="text-blue-600 hover:text-blue-500 font-semibold">
                                        Contact support
                                    </a>
                                </p>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </AuthLayout>
    );
}