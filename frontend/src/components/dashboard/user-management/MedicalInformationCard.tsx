import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';

export default function MedicalInformationCard() {
    const [emergencyContact, setEmergencyContact] = useState('');
    const [emergencyPhone, setEmergencyPhone] = useState('');
    const [medicalAid, setMedicalAid] = useState('');
    const [plan, setPlan] = useState('');
    const [number, setNumber] = useState('');
    const [conditions, setConditions] = useState('');
    const [allergies, setAllergies] = useState('');
    const [medications, setMedications] = useState('');

    const handleSave = () => {
        // API call to update medical info
    };

    return (
        <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Emergency & Medical Information</h2>
            <div className="space-y-4">
                <Input type="text" placeholder="Emergency Contact" value={emergencyContact} onChange={(e) => setEmergencyContact(e.target.value)} />
                <Input type="tel" placeholder="Emergency Phone" value={emergencyPhone} onChange={(e) => setEmergencyPhone(e.target.value)} />
                <Input type="text" placeholder="Medical Aid Provider" value={medicalAid} onChange={(e) => setMedicalAid(e.target.value)} />
                <Input type="text" placeholder="Medical Aid Plan" value={plan} onChange={(e) => setPlan(e.target.value)} />
                <Input type="text" placeholder="Medical Aid Number" value={number} onChange={(e) => setNumber(e.target.value)} />
                <Textarea placeholder="Medical Conditions" value={conditions} onChange={(e) => setConditions(e.target.value)} />
                <Textarea placeholder="Allergies" value={allergies} onChange={(e) => setAllergies(e.target.value)} />
                <Textarea placeholder="Medications" value={medications} onChange={(e) => setMedications(e.target.value)} />
            </div>
            <div className="flex space-x-2 mt-4">
                <Button onClick={handleSave}>Save changes</Button>
                <Button variant="outline" onClick={() => {}}>Cancel</Button>
            </div>
        </Card>
    );
}