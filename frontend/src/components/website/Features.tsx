
import { Bot, Brain, FileText, StickyNote } from "lucide-react";

export default function Features() {
    const features = [
        {
            icon: <FileText className="h-10 w-10 text-blue-600" />,
            title: "Document Management",
            description:
                "Organise, secure and share documents with teams and clients from one central workspace.",
        },
        {
            icon: <StickyNote className="h-10 w-10 text-purple-600" />,
            title: "Skhokho Notes",
            description:
                "Capture ideas, meeting minutes and knowledge. Tag, search and collaborate effortlessly.",
        },
        {
            icon: <Bot className="h-10 w-10 text-green-600" />,
            title: "AI Chatbot",
            description:
                "Talk to your business software with natural language prompts, e.g. ask the AI to create an invoice.",
        },
        {
            icon: <Brain className="h-10 w-10 text-pink-600" />,
            title: "Embedded AI",
            description:
                "Smart AI tools embedded at all levels, from notes to assisting with market research and competitor insights.",
        },
    ];

    return (
        <section
            id="features"
            className="bg-gradient-to-br from-blue-100 via-blue-200 to-blue-300 py-20"
        >
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900">
                        Your{" "}
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                            AI-Powered
                        </span>{" "}
                        Business Software
                    </h2>
                    <p className="mt-4 text-gray-700 max-w-2xl mx-auto">
                        Tools designed to help you work smarter, not harder.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((feature, idx) => (
                        <div
                            key={idx}
                            className="bg-white rounded-xl shadow-md hover:shadow-xl transition transform hover:-translate-y-1 p-6 text-center"
                        >
                            <div className="flex items-center justify-center mb-4">
                                {feature.icon}
                            </div>
                            <h3 className="text-lg font-semibold mb-2 text-gray-900">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 mb-4">{feature.description}</p>
                            <a
                                href="#"
                                className="text-blue-600 font-medium hover:underline"
                            >
                                Learn More →
                            </a>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
