"use client";

import AddressInformationCard from './AddressInformationCard';
import BankingInformationCard from './BankingInformationCard';
import EmployeeDocumentsCard from './EmployeeDocumentsCard';
import EmployeeInformationCard from './EmployeeInformationCard';
import MedicalInformationCard from './MedicalInformationCard';
import PasswordChangeCard from './PasswordChangeCard';

import ProfileSidebarCard from './ProfileSidebarCard';

export default function ProfileWrapper() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="h1-title">Profile Settings</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <ProfileSidebarCard />
                <EmployeeInformationCard />
                <AddressInformationCard />
                <MedicalInformationCard />
                <BankingInformationCard />
                <PasswordChangeCard />
            </div>
        </div>
    );
}
