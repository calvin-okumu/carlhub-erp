import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import { useProfile } from '@/hooks/useProfile';

export default function MedicalInformationCard() {
    const { profile, updateProfile } = useProfile();
    const [emergencyContact, setEmergencyContact] = useState('');
    const [emergencyPhone, setEmergencyPhone] = useState('');
    const [medicalAid, setMedicalAid] = useState('');
    const [plan, setPlan] = useState('');
    const [number, setNumber] = useState('');
    const [conditions, setConditions] = useState('');
    const [allergies, setAllergies] = useState('');
    const [medications, setMedications] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        if (profile) {
            setEmergencyContact(profile.emergency_contact || '');
            setEmergencyPhone(profile.emergency_phone || '');
            setMedicalAid(profile.medical_aid_provider || '');
            setPlan(profile.medical_aid_plan || '');
            setNumber(profile.medical_aid_number || '');
            setConditions(profile.medical_conditions || '');
            setAllergies(profile.allergies || '');
            setMedications(profile.medications || '');
        }
    }, [profile]);

    const handleSave = async () => {
        try {
            await updateProfile({
                emergency_contact: emergencyContact,
                emergency_phone: emergencyPhone,
                medical_aid_provider: medicalAid,
                medical_aid_plan: plan,
                medical_aid_number: number,
                medical_conditions: conditions,
                allergies: allergies,
                medications: medications,
            });
            setSuccessMessage('Medical information updated successfully');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to update medical information');
        }
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
             {successMessage && (
                 <div className="mt-4 p-2 bg-green-100 text-green-800 rounded">
                     {successMessage}
                 </div>
             )}
        </Card>
    );
}