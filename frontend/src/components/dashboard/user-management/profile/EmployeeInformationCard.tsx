import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useProfile } from '@/hooks/useProfile';

export default function EmployeeInformationCard() {
    const { profile, updateProfile } = useProfile();
    const [idNumber, setIdNumber] = useState('');
    const [employeeNumber, setEmployeeNumber] = useState('');
    const [taxNumber, setTaxNumber] = useState('');
    const [phone, setPhone] = useState('');
    const [birthday, setBirthday] = useState('');
    const [linkedin, setLinkedin] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        if (profile) {
            setIdNumber(profile.employee_id || '');
            setEmployeeNumber(profile.employee_number || '');
            setTaxNumber(profile.tax_number || '');
            setPhone(profile.phone || '');
            setBirthday(profile.hire_date || '');
            setLinkedin(profile.linkedin_profile || '');
        }
    }, [profile]);

    const handleSave = async () => {
        try {
            await updateProfile({
                employee_id: idNumber,
                employee_number: employeeNumber,
                tax_number: taxNumber,
                phone: phone,
                hire_date: birthday,
                linkedin_profile: linkedin,
            });
            setSuccessMessage('Employee information updated successfully');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to update employee information');
        }
    };

    return (
        <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Employee Information</h2>
            <div className="space-y-4">
                <Input type="text" placeholder="ID Number" value={idNumber} onChange={(e) => setIdNumber(e.target.value)} className="w-full p-2 border" />
                <Input type="text" placeholder="Employee Number" value={employeeNumber} onChange={(e) => setEmployeeNumber(e.target.value)} className="w-full p-2 border" />
                <Input type="text" placeholder="Tax Number" value={taxNumber} onChange={(e) => setTaxNumber(e.target.value)} className="w-full p-2 border" />
                <Input type="tel" placeholder="Phone Number" value={phone} onChange={(e) => setPhone(e.target.value)} className="w-full p-2 border" />
                <Input type="date" value={birthday} onChange={(e) => setBirthday(e.target.value)} className="w-full p-2 border" />
                <Input type="url" placeholder="LinkedIn Profile" value={linkedin} onChange={(e) => setLinkedin(e.target.value)} className="w-full p-2 border" />
            </div>
             <div className="flex space-x-2 mt-4">
                 <Button onClick={handleSave}>Save changes</Button>
                 <Button variant="outline" onClick={() => { }}>Cancel</Button>
             </div>
             {successMessage && (
                 <div className="mt-4 p-2 bg-green-100 text-green-800 rounded">
                     {successMessage}
                 </div>
             )}
        </Card>
    );
}
