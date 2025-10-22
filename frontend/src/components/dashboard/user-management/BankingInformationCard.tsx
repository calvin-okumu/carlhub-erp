import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';

export default function BankingInformationCard() {
    const [bankName, setBankName] = useState('');
    const [accountNumber, setAccountNumber] = useState('');
    const [branchCode, setBranchCode] = useState('');
    const [accountType, setAccountType] = useState('');
    const [routingNumber, setRoutingNumber] = useState('');
    const [swiftCode, setSwiftCode] = useState('');

    const handleSave = () => {
        // API call to update banking info
    };

    return (
        <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Banking Information</h2>
            <div className="space-y-4">
                <Input type="text" placeholder="Bank Name" value={bankName} onChange={(e) => setBankName(e.target.value)} />
                <Input type="text" placeholder="Account Number" value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)} />
                <Input type="text" placeholder="Branch Code" value={branchCode} onChange={(e) => setBranchCode(e.target.value)} />
                <Select value={accountType} onChange={(e) => setAccountType(e.target.value)}>
                    <option>Checking</option>
                    <option>Savings</option>
                </Select>
                <Input type="text" placeholder="Routing Number" value={routingNumber} onChange={(e) => setRoutingNumber(e.target.value)} />
                <Input type="text" placeholder="SWIFT Code" value={swiftCode} onChange={(e) => setSwiftCode(e.target.value)} />
            </div>
            <div className="flex space-x-2 mt-4">
                <Button onClick={handleSave}>Save changes</Button>
                <Button variant="outline" onClick={() => {}}>Cancel</Button>
            </div>
        </Card>
    );
}