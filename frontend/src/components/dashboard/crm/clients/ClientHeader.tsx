import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import StatCard from '@/components/ui/StatCard';
import { UserCheck, UserPlus, Users } from 'lucide-react';

interface ClientHeaderProps {
    onAddClient: () => void;
    searchValue: string;
    onSearchChange: (value: string) => void;
    metrics?: {
        totalClients: number;
        activeClients: number;
        prospects: number;
        newClientsThisMonth: number;
    };
    loading?: boolean;
    error?: string | null;
}

export default function ClientHeader({
    onAddClient,
    searchValue,
    onSearchChange,
    metrics,
    loading = false,
    error = null
}: ClientHeaderProps) {
    // Default metrics if not provided
    const defaultMetrics = {
        totalClients: 0,
        activeClients: 0,
        prospects: 0,
        newClientsThisMonth: 0,
    };

    const {
        totalClients,
        activeClients,
        prospects,
        newClientsThisMonth
    } = metrics || defaultMetrics;

    const handleAddClient = () => {
        onAddClient();
    };

    return (
        <div className="space-y-6">
            {/* Error Display */}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <span className="font-medium">Error loading client metrics:</span>
                        <span className="ml-2">{error}</span>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Clients"
                    value={loading ? "..." : totalClients}
                    icon={Users}
                    loading={loading}
                    color="blue"
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Active Clients"
                    value={loading ? "..." : activeClients}
                    icon={UserCheck}
                    loading={loading}
                    color="green"
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="Prospects"
                    value={loading ? "..." : prospects}
                    icon={UserPlus}
                    loading={loading}
                    color="yellow"
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
                <StatCard
                    title="New This Month"
                    value={loading ? "..." : newClientsThisMonth}
                    icon={UserPlus}
                    loading={loading}
                    color="purple"
                    className="shadow-lg hover:shadow-xl transition-shadow duration-300"
                />
            </div>
            <div className="flex justify-between items-center">
                <Input
                    type="text"
                    placeholder="Search clients..."
                    value={searchValue}
                    onChange={(e) => onSearchChange(e.target.value)}
                    className="max-w-xs"
                />
                <Button onClick={handleAddClient}>
                    + Add Client
                </Button>
            </div>
        </div>
    );
};


