
import Card from '@/components/ui/Card';
import { useProfile } from '@/hooks/useProfile';
import { User, Mail, Calendar, Briefcase, Building } from 'lucide-react';
import Loader from '@/components/shared/Loader';

export default function ProfileDetailsCard() {
    const { profile, loading, error } = useProfile();

    if (loading) {
        return (
            <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Profile Details</h2>
                </div>
                <Loader />
            </Card>
        );
    }

    if (error || !profile) {
        return (
            <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Profile Details</h2>
                </div>
                <div className="text-sm text-red-500">{error || "Profile not available"}</div>
            </Card>
        );
    }

    const fields = [
        { label: 'Name', value: `${profile.first_name} ${profile.last_name}`, icon: User },
        { label: 'Email', value: profile.email, icon: Mail },
        { label: 'Job', value: profile.job_title || 'Not specified', icon: Briefcase },
        { label: 'Organization', value: profile.organization || 'Not specified', icon: Building },
        { label: 'Joined', value: new Date(profile.date_joined).toLocaleDateString(), icon: Calendar },
    ];

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Profile Details</h2>
            </div>

            <div className="space-y-3 text-sm">
                {fields.map(({ label, value, icon: Icon }) => (
                    <div key={label} className="flex items-center space-x-3">
                        <Icon className="h-4 w-4 text-gray-500" />
                        <div>
                            <strong className="capitalize">{label}:</strong> {value}
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    );
}
