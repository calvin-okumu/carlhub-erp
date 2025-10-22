
import Image from "next/image";
import { CheckCircle } from "lucide-react";

export default function WhySkhokho() {
    const points = [
        {
            title: "Built for Growing Small Businesses",
            description:
                "Powerful, affordable and easy to use. Carlhub combines CRM, project management, accounting and HR in a single intuitive dashboard—with strong data security and AWS encryption.",
        },
        {
            title: "Collaborate Anywhere",
            description:
                "Share files, notes and tasks with your team or clients in real time—Collaboration Software designed for small teams.",
        },
        {
            title: "Actionable Insights",
            description:
                "AI analytics turn your data into clear, practical business guidance.",
        },
        {
            title: "Secure by Design",
            description:
                "Bank-level encryption on AWS and daily backups protect your information.",
        },
    ];

    return (
        <section id="platform" className="bg-gray-50 py-20">
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <h2 className="text-3xl font-bold text-center mb-12">
                    Grow your business with{" "}
                    <span className="text-blue-600">Carlhub</span>
                </h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Left: Image */}
                    <div className="order-2 lg:order-1">
                        <Image
                            src="/whycarlhub.svg"
                            alt="Why Carlhub"
                            width={600}
                            height={400}
                            className="w-full rounded-lg shadow-lg"
                        />
                    </div>

                    {/* Right: Content */}
                    <div className="order-1 lg:order-2">
                        <h3 className="text-2xl font-semibold mb-8">Why Carlhub</h3>
                        <div className="space-y-6">
                            {points.map((point, idx) => (
                                <div key={idx} className="flex items-start space-x-3">
                                    <CheckCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
                                    <div>
                                        <h4 className="text-lg font-semibold mb-1">{point.title}</h4>
                                        <p className="text-gray-600">{point.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
