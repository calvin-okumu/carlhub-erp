"use client";

import AddressInformationCard from './AddressInformationCard';
import BankingInformationCard from './BankingInformationCard';
import EmployeeDocumentsCard from './EmployeeDocumentsCard';
import EmployeeInformationCard from './EmployeeInformationCard';
import MedicalInformationCard from './MedicalInformationCard';
import PasswordChangeCard from './PasswordChangeCard';
import PersonalInformationCard from './PersonalInformationCard';
import ProfileSidebarCard from './ProfileSidebarCard';

export default function ProfileWrapper() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <h1 className="h1-title">Profile Settings</h1>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-6">
                    <ProfileSidebarCard />
                    <PasswordChangeCard />
                    <EmployeeDocumentsCard />
                </div>
                <div className="space-y-6">
                    <PersonalInformationCard />
                    <AddressInformationCard />
                    <EmployeeInformationCard />
                    <MedicalInformationCard />
                    <BankingInformationCard />
                </div>
            </div>
        </div>
    );
}
