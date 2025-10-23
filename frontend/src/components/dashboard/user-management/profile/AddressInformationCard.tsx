import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { useProfile } from '@/hooks/useProfile';

export default function AddressInformationCard() {
    const { profile, updateProfile } = useProfile();
    const [street, setStreet] = useState('');
    const [city, setCity] = useState('');
    const [state, setState] = useState('');
    const [postalCode, setPostalCode] = useState('');
    const [country, setCountry] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

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
            setSuccessMessage('Address information updated successfully');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to update address information');
        }
    };

    return (
        <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Address Information</h2>
            <div className="space-y-4">
                <Input type="text" placeholder="Street Address" value={street} onChange={(e) => setStreet(e.target.value)} />
                <Input type="text" placeholder="City" value={city} onChange={(e) => setCity(e.target.value)} />
                <Input type="text" placeholder="State/Province" value={state} onChange={(e) => setState(e.target.value)} />
                <Input type="text" placeholder="Postal Code" value={postalCode} onChange={(e) => setPostalCode(e.target.value)} />
                <Select value={country} onChange={(e) => setCountry(e.target.value)}>
                    <option>USA</option>
                    <option>Canada</option>
                </Select>
            </div>
             <div className="flex space-x-2 mt-4">
                 <Button onClick={handleSave}>Save changes</Button>
                 <Button variant="outline" onClick={() => {}}>Cancel</Button>
             </div>
             {successMessage && (
                 <div className="mt-4 p-2 bg-green-100 text-green-800 rounded">
                     {successMessage}
                 </div>
             )}
        </Card>
    );
}