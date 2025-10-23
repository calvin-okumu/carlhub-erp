import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';

export default function EmployeeDocumentsCard() {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [documents, setDocuments] = useState([]);

    const handleUpload = () => {
        // Handle file upload
    };

    return (
        <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Employee Documents</h2>
            <div className="mb-4">
                <input type="file" className="mb-2" />
                <p className="text-sm text-gray-500 mb-2">Max size: 10MB, Formats: PDF, DOC</p>
                <Input type="text" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} className="mb-2" />
                <Textarea placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} className="mb-2" />
                <div className="flex space-x-2">
                    <Button onClick={handleUpload}>Upload Document</Button>
                    <Button variant="outline" onClick={() => {}}>Reset</Button>
                </div>
            </div>
            <div>
                <h3 className="font-medium mb-2">My Documents</h3>
                {documents.length === 0 ? (
                    <p className="text-gray-500">No documents uploaded yet</p>
                ) : (
                    <ul>{/* List documents */}</ul>
                )}
            </div>
        </Card>
    );
}