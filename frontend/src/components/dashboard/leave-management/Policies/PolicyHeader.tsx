import StatCard from "@/components/ui/StatCard"
import { Calendar, DollarSign, Heart } from "lucide-react"

export const PolicyHeader = () => {
    return (
        <div className="space-y-2">
            <div>
                <h2 className="text-xl font-bold text-gray-900 mt-6 mb-4">Leave Balances</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard
                    title="Annual Leave"
                    value="10/10 days"
                    icon={Calendar}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Sick Leave"
                    value="10/10 days"
                    icon={Heart}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Unpaid Leave"
                    value="10/10 days"
                    icon={DollarSign}
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
            </div>
        </div>
    )
}

