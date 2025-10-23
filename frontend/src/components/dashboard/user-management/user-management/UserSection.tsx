"use client";
import React, { useState } from 'react';
import { UserHeader } from "./UserHeader";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import Card from "@/components/ui/Card";
import Loader from "@/components/shared/Loader";
import ActiveEmployeeTable from "./Employees/ActiveEmployeeTable";
import ActiveUsersTable from "./Employees/ActiveUsersTable";
import InvitesTable from "./Employees/InvitesTable";
import EmployeeModal from "./Employees/EmployeeModal";

export const UserSection = () => {
    const [activeTab, setActiveTab] = useState<'invites' | 'activeUsers' | 'employees'>('employees');
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [loading, setLoading] = useState(false);

    const totalItems = 0; // Update with actual data length
    const entriesPerPage = 10; // Fixed entries per page

    const handleTabChange = (tab: 'invites' | 'activeUsers' | 'employees') => {
        setActiveTab(tab);
        setCurrentPage(1);
    };

    const handleAddEmployee = () => {
        setModalMode('add');
        setIsModalOpen(true);
    };

    return (
        <div className="p-6">
            <UserHeader activeTab={activeTab} onTabChange={handleTabChange} />
            <Card className="mt-4">
                <div className="flex justify-between items-center mb-4">
                    {activeTab === 'employees' && (
                        <Button onClick={handleAddEmployee} className="bg-blue-600 text-white">
                            + Add Employee
                        </Button>
                    )}
                    <div className="flex items-center space-x-4">
                        <Input
                            placeholder={`Search ${activeTab === 'invites' ? 'invites' : activeTab === 'activeUsers' ? 'users' : 'employees'}`}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <Select>
                            <option value="export">Export</option>
                        </Select>
                    </div>
                </div>
                 {loading ? (
                     <Loader />
                 ) : activeTab === 'invites' ? (
                     <InvitesTable
                         searchTerm={searchTerm}
                         entriesPerPage={entriesPerPage}
                         currentPage={currentPage}
                         invites={[]}
                         totalPages={Math.ceil(totalItems / entriesPerPage)}
                         onPageChange={setCurrentPage}
                         itemsPerPage={entriesPerPage}
                         totalItems={totalItems}
                     />
                 ) : activeTab === 'activeUsers' ? (
                     <ActiveUsersTable
                         searchTerm={searchTerm}
                         entriesPerPage={entriesPerPage}
                         currentPage={currentPage}
                         users={[]}
                         totalPages={Math.ceil(totalItems / entriesPerPage)}
                         onPageChange={setCurrentPage}
                         itemsPerPage={entriesPerPage}
                         totalItems={totalItems}
                     />
                 ) : (
                     <ActiveEmployeeTable
                         searchTerm={searchTerm}
                         entriesPerPage={entriesPerPage}
                         currentPage={currentPage}
                         employees={[]}
                         totalPages={Math.ceil(totalItems / entriesPerPage)}
                         onPageChange={setCurrentPage}
                         itemsPerPage={entriesPerPage}
                         totalItems={totalItems}
                     />
                 )}
             </Card>
             {activeTab === 'employees' && (
                 <EmployeeModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} mode={modalMode} />
             )}
         </div>
     );
};

