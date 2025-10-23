export default function Pricing() {
    const plans = [
        {
            name: "Free",
            price: "$0 / month",
            features: [
                "Up to 2 Users",
                "Limited Clients",
                "Limited Invoices",
                "Limited Quotes",
                "5GB Free Storage",
                "AI Credits ($2)",
                "Basic CRM & Project Management",
                "Community Support",
            ],
        },
        {
            name: "Business",
            price: "$20 / user / month",
            features: [
                "Everything in Free",
                "20GB Storage per user",
                "All Application Features",
                "AI Credits ($10)",
                "Unlimited Users",
                "Unlimited Clients & Invoices",
                "Email Support",
                "WhatsApp Integration",
            ],
        },
        {
            name: "Business Pro",
            price: "$30 / user / month",
            features: [
                "Everything in Business",
                "50GB Storage per user",
                "All Application Features",
                "AI Credits ($20)",
                "Unlimited Users",
                "API & Zapier Integration",
                "Priority Email Support (48hr turnaround)",
            ],
        },
    ];

    return (
        <section id="pricing" className="py-16 bg-gray-50">
            <div className="max-w-7xl mx-auto px-4">
                <h2 className="text-3xl font-bold text-center mb-6">Simple Pricing</h2>
                <h3 className="text-xl font-medium text-center mb-8">Transparent Plans</h3>
                <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
                    No setup fees, no hidden costs—just choose the plan that fits your team and grow at your own pace.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {plans.map((plan, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-2xl shadow-md p-6 hover:shadow-lg transition"
                        >
                            <h4 className="text-xl font-semibold mb-2 text-center">{plan.name}</h4>
                            <p className="text-2xl font-bold mb-6 text-center">{plan.price}</p>
                            <ul className="text-gray-600 space-y-2 mb-6">
                                {plan.features.map((feature, i) => (
                                    <li key={i} className="flex items-start">
                                        <span className="mr-2 text-indigo-600">✔</span>
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                            <div className="text-center">
                                <a
                                    href="#"
                                    className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
                                >
                                    Get Started
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
