import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';

export default function AddressInformationCard() {
    const [street, setStreet] = useState('');
    const [city, setCity] = useState('');
    const [state, setState] = useState('');
    const [postalCode, setPostalCode] = useState('');
    const [country, setCountry] = useState('');

    const handleSave = () => {
        // API call to update address
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
        </Card>
    );
}