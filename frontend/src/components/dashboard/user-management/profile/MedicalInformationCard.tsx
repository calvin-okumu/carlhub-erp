import Loader from '@/components/shared/Loader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import { useProfile } from '@/hooks/useProfile';
import { Building, FileText, Hash, Phone, User } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function MedicalInformationCard() {
    const { profile, loading, error, updateProfile } = useProfile();
    const [isEditing, setIsEditing] = useState(false);
    const [emergencyContact, setEmergencyContact] = useState('');
    const [emergencyPhone, setEmergencyPhone] = useState('');
    const [medicalAid, setMedicalAid] = useState('');
    const [plan, setPlan] = useState('');
    const [number, setNumber] = useState('');
    const [conditions, setConditions] = useState('');
    const [allergies, setAllergies] = useState('');
    const [medications, setMedications] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

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
            setIsEditing(false);
            setSuccessMessage('Medical information updated successfully');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (_err) {
            setErrorMessage('Unable to update medical information. Please try again.');
            setTimeout(() => setErrorMessage(''), 5000);
        }
    };

    const handleCancel = () => {
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
        setIsEditing(false);
    };

    if (loading) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Emergency & Medical Information</h2>
                <Loader />
            </Card>
        );
    }

    if (error || !profile) {
        return (
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Emergency & Medical Information</h2>
                <div className="text-sm text-red-500">{error || "Unable to load medical information"}</div>
            </Card>
        );
    }

    return (
        <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Emergency & Medical Information</h2>
                {!isEditing && (
                    <Button onClick={() => setIsEditing(true)} variant="secondary" size="sm">
                        Edit
                    </Button>
                )}
            </div>

            <div className="space-y-4">
                {/* Emergency Contact */}
                <div className="flex items-center space-x-3">
                    <User className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Emergency Contact"
                            value={emergencyContact}
                            onChange={(e) => setEmergencyContact(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{emergencyContact || 'Not specified'}</span>
                    )}
                </div>

                {/* Emergency Phone */}
                <div className="flex items-center space-x-3">
                    <Phone className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="tel"
                            placeholder="Emergency Phone"
                            value={emergencyPhone}
                            onChange={(e) => setEmergencyPhone(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{emergencyPhone || 'Not specified'}</span>
                    )}
                </div>

                {/* Medical Aid Provider */}
                <div className="flex items-center space-x-3">
                    <Building className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Medical Aid Provider"
                            value={medicalAid}
                            onChange={(e) => setMedicalAid(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{medicalAid || 'Not specified'}</span>
                    )}
                </div>

                {/* Medical Aid Plan */}
                <div className="flex items-center space-x-3">
                    <FileText className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Medical Aid Plan"
                            value={plan}
                            onChange={(e) => setPlan(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{plan || 'Not specified'}</span>
                    )}
                </div>

                {/* Medical Aid Number */}
                <div className="flex items-center space-x-3">
                    <Hash className="h-4 w-4 text-gray-500" />
                    {isEditing ? (
                        <Input
                            type="text"
                            placeholder="Medical Aid Number"
                            value={number}
                            onChange={(e) => setNumber(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{number || 'Not specified'}</span>
                    )}
                </div>

                {/* Medical Conditions */}
                <div className="flex items-start space-x-3">
                    <FileText className="h-4 w-4 text-gray-500 mt-1" />
                    {isEditing ? (
                        <Textarea
                            placeholder="Medical Conditions"
                            value={conditions}
                            onChange={(e) => setConditions(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{conditions || 'Not specified'}</span>
                    )}
                </div>

                {/* Allergies */}
                <div className="flex items-start space-x-3">
                    <FileText className="h-4 w-4 text-gray-500 mt-1" />
                    {isEditing ? (
                        <Textarea
                            placeholder="Allergies"
                            value={allergies}
                            onChange={(e) => setAllergies(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{allergies || 'Not specified'}</span>
                    )}
                </div>

                {/* Medications */}
                <div className="flex items-start space-x-3">
                    <FileText className="h-4 w-4 text-gray-500 mt-1" />
                    {isEditing ? (
                        <Textarea
                            placeholder="Medications"
                            value={medications}
                            onChange={(e) => setMedications(e.target.value)}
                            className="flex-1"
                        />
                    ) : (
                        <span className="flex-1">{medications || 'Not specified'}</span>
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
