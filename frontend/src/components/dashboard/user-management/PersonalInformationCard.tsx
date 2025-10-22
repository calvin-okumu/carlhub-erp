import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { useProfile } from '@/hooks/useProfile';
import { User, Briefcase, Languages } from 'lucide-react';
import Loader from '@/components/shared/Loader';

export default function PersonalInformationCard() {
    const { profile, loading, error } = useProfile();
    const [isEditing, setIsEditing] = useState(false);
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [jobTitle, setJobTitle] = useState('');
    const [language, setLanguage] = useState('English');

    useEffect(() => {
        if (profile) {
            setFirstName(profile.first_name || '');
            setLastName(profile.last_name || '');
            setJobTitle(profile.job || '');
            setLanguage('English'); // Default, can be extended
        }
    }, [profile]);

    const handleSave = () => {
        // TODO: API call to update personal info
        setIsEditing(false);
    };

    const handleCancel = () => {
        if (profile) {
            setFirstName(profile.first_name || '');
            setLastName(profile.last_name || '');
            setJobTitle(profile.job || '');
        }
        setIsEditing(false);
    };

    if (loading) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Personal Information</h2>
                <Loader />
            </Card>
        );
    }

    if (error || !profile) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Personal Information</h2>
                <div className="text-sm text-red-500">{error || "Unable to load personal information"}</div>
            </Card>
        );
    }

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Personal Information</h2>
                {!isEditing && (
                    <Button onClick={() => setIsEditing(true)} variant="outline" size="sm">
                        Edit
                    </Button>
                )}
            </div>

            <div className="space-y-4">
                {/* First Name */}
                <div className="flex items-center space-x-3">
                    <User className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="First Name"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{firstName || 'Not specified'}</span>
                    )}
                </div>

                {/* Last Name */}
                <div className="flex items-center space-x-3">
                    <User className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Last Name"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{lastName || 'Not specified'}</span>
                    )}
                </div>

                {/* Job Title */}
                <div className="flex items-center space-x-3">
                    <Briefcase className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Job Title"
                            value={jobTitle}
                            onChange={(e) => setJobTitle(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{jobTitle || 'Not specified'}</span>
                    )}
                </div>

                {/* Language */}
                <div className="flex items-center space-x-3">
                    <Languages className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="flex-1"
                        >
                            <option value="English">English</option>
                            <option value="Spanish">Spanish</option>
                        </Select>
                    ) : (
                        <span className="flex-1">{language}</span>
                    )}
                </div>
            </div>

            {isEditing && (
                <div className="flex space-x-2 mt-4">
                    <Button onClick={handleSave}>Save Changes</Button>
                    <Button variant="outline" onClick={handleCancel}>Cancel</Button>
                </div>
            )}
        </Card>
    );
}