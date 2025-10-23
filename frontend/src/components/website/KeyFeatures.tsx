export default function KeyFeatures() {
    const features = [
        {
            title: "Data Security",
            description:
                "Protect your data with bank-level encryption, continuous backups, and granular access controls on our secure AWS-powered platform.",
        },
        {
            title: "Project & CRM",
            description:
                "Plan tasks, set milestones, and track progress while managing leads and relationships—project management and CRM together in one platform.",
        },
        {
            title: "Invoicing & Billing",
            description:
                "Generate branded invoices, accept online payments, and reconcile accounts automatically.",
        },
        {
            title: "Document Management & Collaboration",
            description:
                "Share and collaborate on documents and notes with your team in one place—keeping everyone aligned.",
        },
        {
            title: "AI Content Generator",
            description:
                "Create proposals, reports, and marketing copy in seconds with GPT-powered templates.",
        },
        {
            title: "WhatsApp Integration",
            description:
                "Send quotes, invoices, and updates directly from your favorite messaging app.",
        },
    ];

    return (
        <section className="bg-blue-300 py-16">
            <div className="max-w-7xl mx-auto px-4">
                <h2 className="text-3xl font-bold text-center mb-6">Key Features</h2>
                <h3 className="text-xl text-center font-medium mb-8">
                    What Carlhub Delivers
                </h3>
                <p className="text-center text-gray-700 mb-12 max-w-3xl mx-auto">
                    Everything you need to run, grow, and scale your small business
                    from a single login—secure platform with internationalisation.
                    CRM and project management software, together.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-2xl shadow-md p-6 text-center hover:shadow-lg transition"
                        >
                            <h4 className="text-lg font-semibold mb-2">
                                {feature.title}
                            </h4>
                            <p className="text-gray-600 mb-4">{feature.description}</p>
                            <a
                                href="#"
                                className="text-indigo-600 font-medium hover:underline"
                            >
                                Learn More
                            </a>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
