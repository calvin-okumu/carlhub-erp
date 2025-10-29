import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import { useEffect, useState } from 'react';

import Loader from '@/components/shared/Loader';
import { useProfile } from '@/hooks/useProfile';
import { Building, Globe, Hash, MapPin } from 'lucide-react';

export default function AddressInformationCard() {
    const { profile, loading, error, updateProfile } = useProfile();
    const [isEditing, setIsEditing] = useState(false);
    const [street, setStreet] = useState('');
    const [city, setCity] = useState('');
    const [state, setState] = useState('');
    const [postalCode, setPostalCode] = useState('');
    const [country, setCountry] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        if (profile) {
            setStreet(profile.street_address || '');
            setCity(profile.city || '');
            setState(profile.state_province || '');
            setPostalCode(profile.postal_code || '');
            setCountry(profile.country || '');
        }
    }, [profile]);

    const handleSave = async () => {
        try {
            await updateProfile({
                street_address: street,
                city: city,
                state_province: state,
                postal_code: postalCode,
                country: country,
            });
            setIsEditing(false);
            setSuccessMessage('Address information updated successfully');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            setErrorMessage('Unable to update address information. Please try again.');
            setTimeout(() => setErrorMessage(''), 5000);
        }
    };

    const handleCancel = () => {
        if (profile) {
            setStreet(profile.street_address || '');
            setCity(profile.city || '');
            setState(profile.state_province || '');
            setPostalCode(profile.postal_code || '');
            setCountry(profile.country || '');
        }
        setIsEditing(false);
    };

    if (loading) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Address Information</h2>
                <Loader />
            </Card>
        );
    }

    if (error || !profile) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Address Information</h2>
                <div className="text-sm text-red-500">{error || "Unable to load address information"}</div>
            </Card>
        );
    }

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Address Information</h2>
                {!isEditing && (
                    <Button onClick={() => setIsEditing(true)} variant="secondary" size="sm">
                        Edit
                    </Button>
                )}
            </div>

            <div className="space-y-4">
                {/* Street Address */}
                <div className="flex items-center space-x-3">
                    <MapPin className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Street Address"
                            value={street}
                            onChange={(e) => setStreet(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{street || 'Not specified'}</span>
                    )}
                </div>

                {/* City */}
                <div className="flex items-center space-x-3">
                    <Building className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="City"
                            value={city}
                            onChange={(e) => setCity(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{city || 'Not specified'}</span>
                    )}
                </div>

                {/* State/Province */}
                <div className="flex items-center space-x-3">
                    <Building className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="State/Province"
                            value={state}
                            onChange={(e) => setState(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{state || 'Not specified'}</span>
                    )}
                </div>

                {/* Postal Code */}
                <div className="flex items-center space-x-3">
                    <Hash className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Postal Code"
                            value={postalCode}
                            onChange={(e) => setPostalCode(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{postalCode || 'Not specified'}</span>
                    )}
                </div>

                {/* Country */}
                <div className="flex items-center space-x-3">
                    <Globe className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Country"
                            value={country}
                            onChange={(e) => setCountry(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{country || 'Not specified'}</span>
                    )}
                </div>
            </div>

            {isEditing && (
                <div className="flex space-x-2 mt-4">
                    <Button onClick={handleSave}>Save Changes</Button>
                    <Button variant="secondary" onClick={handleCancel}>Cancel</Button>
                </div>
            )}
            {successMessage && (
                <div className="mt-4 p-2 bg-green-100 text-green-800 rounded">
                    {successMessage}
                </div>
            )}
            {errorMessage && (
                <div className="mt-4 p-2 bg-red-100 text-red-800 rounded">
                    {errorMessage}
                </div>
            )}
        </Card>
    );
}
