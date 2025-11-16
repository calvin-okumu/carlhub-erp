import Card from "@/components/ui/Card";
import { ChevronDown } from "lucide-react";
import { useState } from "react";

const DropdownCard = ({ title, children }: { title: string; children: React.ReactNode }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <Card className="mt-6">
            <div
                className="flex items-center justify-between cursor-pointer p-4 hover:bg-gray-50 transition-colors"
                onClick={() => setIsOpen(!isOpen)}
            >
                <h2 className="text-xl font-bold text-gray-900">{title}</h2>
                <ChevronDown
                    className={`w-5 h-5 text-gray-500 transition-transform ${isOpen ? "rotate-180" : ""
                        }`}
                />
            </div>

            <div
                className={`overflow-hidden transition-all duration-300 ${isOpen ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
                    }`}
            >
                <div className="px-4 pb-4">{children}</div>
            </div>
        </Card>
    );
};

export const PolicyRules = () => {
    return (
        <div className="space-y-4">
            <DropdownCard title="Leave Types">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li><strong>Annual Leave:</strong> 21 days per year. Accrues monthly.</li>
                    <li><strong>Sick Leave:</strong> 14 days paid, requires medical note after 2 days.</li>
                    <li><strong>Casual Leave:</strong> 7 days per year for urgent personal matters.</li>
                    <li><strong>Maternity Leave:</strong> 90 days, as per employment law.</li>
                    <li><strong>Paternity Leave:</strong> 14 days.</li>
                    <li><strong>Unpaid Leave:</strong> Available upon request and approval.</li>
                </ul>
            </DropdownCard>

            {/* Section 2: General Leave Rules */}
            <DropdownCard title="General Leave Rules">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li>All leave must be applied for through the system.</li>
                    <li>Leave must be approved by your manager before it is valid.</li>
                    <li>Leave cannot be taken if you have a pending disciplinary case.</li>
                    <li>You cannot apply for leave retroactively.</li>
                    <li>Public holidays do not count as leave days.</li>
                </ul>
            </DropdownCard>

            <DropdownCard title="Carry Forward Policy">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li>Up to 7 unused annual leave days can be carried forward.</li>
                    <li>All carried-forward days must be used within the first 3 months of the new year.</li>
                    <li>Unused carried-forward days are forfeited.</li>
                </ul>
            </DropdownCard>

            <DropdownCard title="Leave Application Guidelines">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li>Apply for leave at least 5 days in advance for annual leave.</li>
                    <li>Sick leave must be reported before 9:00 AM on the same day.</li>
                    <li>Emergency leave requires manager notification before submitting the request.</li>
                    <li>Maternity and paternity leave require documentation as per HR policy.</li>
                </ul>
            </DropdownCard>

            <DropdownCard title="Approval Workflow">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li>Employee submits leave request.</li>
                    <li>Direct manager receives and reviews the request.</li>
                    <li>HR is notified of all approved leave.</li>
                    <li>System automatically updates leave balance upon approval.</li>
                </ul>
            </DropdownCard>

            <DropdownCard title="Leave Restrictions">
                <ul className="list-disc pl-6 space-y-1 text-gray-700">
                    <li>You cannot apply for more leave days than you currently have available.</li>
                    <li>Back-to-back long leave may require special approval.</li>
                    <li>Leave during critical project deadlines may be restricted.</li>
                </ul>
            </DropdownCard>
        </div>
    );
};
