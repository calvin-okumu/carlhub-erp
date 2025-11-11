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
import TerminatedEmployeeTable from "./Employees/TerminatedEmployeeTable";
import EmployeeModal from "./Employees/EmployeeModal";
import InviteModal from "./Employees/InviteModal";
import { useEmployees } from "@/hooks/useEmployees";
import { getUsers } from "@/api/users";
import { API_BASE, resendInvitation, deleteInvitation } from "@/api";
import type { UserTenant, User, UserProfile } from "@/api/types";

export const UserSection = () => {
    const [activeTab, setActiveTab] = useState<'invites' | 'activeUsers' | 'employees' | 'groups'>('employees');
    const [employeeSubTab, setEmployeeSubTab] = useState<'active' | 'terminated'>('active');
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedEmployee, setSelectedEmployee] = useState<UserProfile | null>(null);
    const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
    const [groups, setGroups] = useState<Array<{ id: number, name: string }>>([
        { id: 1, name: 'Admin' },
        { id: 2, name: 'Manager' },
        { id: 3, name: 'Employee' },
        { id: 4, name: 'Developer' },
        { id: 5, name: 'Designer' }
    ]);

    const [invites, setInvites] = useState<Array<{
        id: number;
        email: string;
        sentDate: string;
        status: string;
        token: string;
        slug: string;
    }>>([]);
    const [invitesLoading, setInvitesLoading] = useState(false);

    const { employees, loading, createEmployee, updateEmployee, deleteEmployee, refetch } = useEmployees();
    const [users, setUsers] = useState<Array<{
        id: number;
        name: string;
        avatar: string;
        email: string;
        job_title: string;
        last_login: string;
        role: string;
        status: string;
    }>>([]);
    const [usersLoading, setUsersLoading] = useState(false);

    // Separate employees by status
    const activeEmployees = employees.filter(emp => emp.is_active !== false);
    const terminatedEmployees = employees.filter(emp => emp.is_active === false);

    const currentEmployees = employeeSubTab === 'active' ? activeEmployees : terminatedEmployees;
    const totalItems = currentEmployees.length;
    const entriesPerPage = 10; // Fixed entries per page

    const fetchUsers = async () => {
        try {
            setUsersLoading(true);
            const token = localStorage.getItem("access_token");
            if (!token) return;

            const fetchedUsers = await getUsers(token);
            // Transform User[] to the format expected by ActiveUsersTable
            const transformedUsers = fetchedUsers.map(user => ({
                id: user.id,
                name: `${user.first_name} ${user.last_name}`,
                avatar: user.first_name?.[0] || 'U',
                email: user.email,
                job_title: user.job || '',
                last_login: '', // Backend doesn't provide this yet
                role: user.organization || 'User',
                status: user.is_active ? 'active' : 'inactive'
            }));
            setUsers(transformedUsers);
        } catch (error) {
            console.error('Error fetching users:', error);
        } finally {
            setUsersLoading(false);
        }
    };

    const fetchInvites = async () => {
        try {
            setInvitesLoading(true);
            const token = localStorage.getItem("access_token");
            if (!token) return;

            const response = await fetch(`${API_BASE}/invitations/`, {
                headers: {
                    'Authorization': `Token ${token}`,
                }
            });

            if (response.ok) {
                const invitations = await response.json();

                // Handle different response formats (results array or direct array)
                const invitesArray = invitations.results || invitations || [];
                const transformedInvites = invitesArray.map((invite: any) => ({
                    id: invite.id,
                    email: invite.email,
                    sentDate: new Date(invite.created_at).toLocaleDateString(),
                    status: invite.is_used ? 'Used' : invite.email_confirmed ? 'Confirmed' : 'Pending',
                    token: invite.token,
                    slug: invite.slug
                }));
                setInvites(transformedInvites);
            } else {
                console.error('Failed to fetch invites:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error fetching invites:', error);
        } finally {
            setInvitesLoading(false);
        }
    };

    const handleTabChange = (tab: 'invites' | 'activeUsers' | 'employees' | 'groups') => {
        setActiveTab(tab);
        setCurrentPage(1);
        if (tab === 'employees') {
            setEmployeeSubTab('active');
        } else if (tab === 'activeUsers') {
            fetchUsers();
        } else if (tab === 'invites') {
            fetchInvites();
        }
    };

    const handleEmployeeSubTabChange = (subTab: 'active' | 'terminated') => {
        setEmployeeSubTab(subTab);
        setCurrentPage(1);
    };

    const handleAddEmployee = () => {
        setModalMode('add');
        setSelectedEmployee(null);
        setIsModalOpen(true);
    };

    const handleEditEmployee = (employee: { id: number; first_name: string; last_name: string; email: string; phone?: string; job_title?: string; hire_date?: string; is_active?: boolean; }) => {
        setModalMode('edit');
        setSelectedEmployee(employee as UserProfile);
        setIsModalOpen(true);
    };

    const handleSaveEmployee = async (employeeData: UserProfile) => {
        try {
            if (modalMode === 'add') {
                await createEmployee(employeeData);
            } else if (selectedEmployee) {
                await updateEmployee(selectedEmployee.id, employeeData);
            }
            refetch(); // Refresh the employee list
        } catch (error) {
            console.error('Error saving employee:', error);
            throw error; // Re-throw to let the modal handle the error
        }
    };

    const handleTerminateEmployee = async (employee: { id: number; first_name: string; last_name: string; email: string; phone?: string; job_title?: string; hire_date?: string; is_active?: boolean; }) => {
        if (confirm(`Are you sure you want to terminate ${employee.first_name} ${employee.last_name}?`)) {
            try {
                await updateEmployee(employee.id, { is_active: false });
                refetch();
            } catch (error) {
                console.error('Error deleting employee:', error);
                alert('Failed to delete employee');
            }
        }
    };

    const handleInviteMember = () => {
        setIsInviteModalOpen(true);
    };

    const handleInviteSent = () => {
        // Refresh the invites list after sending an invitation
        if (activeTab === 'invites') {
            fetchInvites();
        }
    };



    const handleResendInvite = async (inviteId: number) => {
        try {
            const invite = invites.find(i => i.id === inviteId);
            if (!invite) {
                alert('Invitation not found');
                return;
            }

            await resendInvitation(invite.token);
            alert('Invitation resent successfully!');
            // Refresh the invites list
            fetchInvites();
        } catch (error) {
            console.error('Error resending invitation:', error);
            alert('Failed to resend invitation. Please try again.');
        }
    };

    const handleDeleteInvite = async (inviteId: number) => {
        if (confirm('Are you sure you want to delete this invitation?')) {
            try {
                const token = localStorage.getItem("access_token");
                const invite = invites.find(i => i.id === inviteId);
                if (!invite || !token) {
                    alert('Invitation or authentication token not found');
                    return;
                }

                await deleteInvitation(token, invite.slug);
                alert('Invitation deleted successfully!');
                // Refresh the invites list
                fetchInvites();
            } catch (error) {
                console.error('Error deleting invitation:', error);
                alert('Failed to delete invitation. Please try again.');
            }
        }
    };

    const handleReactivateEmployee = async (employee: { id: number; first_name: string; last_name: string; email: string; phone?: string; job_title?: string; hire_date?: string; is_active?: boolean; }) => {
        try {
            await updateEmployee(employee.id, { is_active: true });
            refetch();
        } catch (error) {
            console.error('Error reactivating employee:', error);
            alert('Failed to reactivate employee');
        }
    };

    const handleDeleteEmployee = async (employee: { id: number; first_name: string; last_name: string; email: string; phone?: string; job_title?: string; hire_date?: string; is_active?: boolean; }) => {
        if (confirm(`Are you sure you want to permanently delete ${employee.first_name} ${employee.last_name}? This action cannot be undone.`)) {
            try {
                await deleteEmployee(employee.id);
                refetch();
            } catch (error) {
                console.error('Error deleting employee:', error);
                alert('Failed to delete employee');
            }
        }
    };

    return (
        <div className="p-6">
            <UserHeader activeTab={activeTab} onTabChange={handleTabChange} />
            <Card className="mt-4">
                <div className="flex justify-between items-center mb-4">
                    {activeTab === 'employees' && (
                        <div className="flex items-center space-x-4">
                            <Button onClick={handleAddEmployee} className="bg-blue-600 text-white">
                                + Add Employee
                            </Button>
                            {/* Employee Sub-tabs */}
                            <div className="flex bg-gray-100 rounded-lg p-1">
                                <button
                                    onClick={() => handleEmployeeSubTabChange('active')}
                                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${employeeSubTab === 'active'
                                            ? 'bg-white text-blue-600 shadow-sm'
                                            : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                >
                                    Active ({activeEmployees.length})
                                </button>
                                <button
                                    onClick={() => handleEmployeeSubTabChange('terminated')}
                                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${employeeSubTab === 'terminated'
                                            ? 'bg-white text-blue-600 shadow-sm'
                                            : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                >
                                    Terminated ({terminatedEmployees.length})
                                </button>
                            </div>
                        </div>
                    )}
                    {activeTab === 'invites' && (
                        <div className="flex items-center space-x-4">
                            <Button onClick={handleInviteMember} className="bg-blue-600 text-white">
                                + Invite Member
                            </Button>
                        </div>
                    )}
                    <div className="flex items-center space-x-4">
                        <Input
                            placeholder={`Search ${activeTab === 'invites' ? 'invites' : activeTab === 'activeUsers' ? 'users' : activeTab === 'groups' ? 'groups' : employeeSubTab === 'active' ? 'active employees' : 'terminated employees'}`}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <Select>
                            <option value="export">Export</option>
                        </Select>
                    </div>
                </div>
                {(loading || usersLoading || invitesLoading) ? (
                    <Loader />
                ) : activeTab === 'invites' ? (
                    <InvitesTable
                        searchTerm={searchTerm}
                        entriesPerPage={entriesPerPage}
                        currentPage={currentPage}
                        invites={invites}
                        totalPages={Math.ceil(invites.length / entriesPerPage)}
                        onPageChange={setCurrentPage}
                        itemsPerPage={entriesPerPage}
                        totalItems={invites.length}
                        onResendInvite={handleResendInvite}
                        onDeleteInvite={handleDeleteInvite}
                    />
                ) : activeTab === 'activeUsers' ? (
                    <ActiveUsersTable
                        searchTerm={searchTerm}
                        entriesPerPage={entriesPerPage}
                        currentPage={currentPage}
                        users={users}
                        totalPages={Math.ceil(users.length / entriesPerPage)}
                        onPageChange={setCurrentPage}
                        itemsPerPage={entriesPerPage}
                        totalItems={users.length}
                    />
                ) : activeTab === 'groups' ? (
                    <div className="p-8 text-center text-gray-500">
                        <p>Groups & Permissions management coming soon...</p>
                    </div>
                ) : employeeSubTab === 'active' ? (
                    <ActiveEmployeeTable
                        searchTerm={searchTerm}
                        entriesPerPage={entriesPerPage}
                        currentPage={currentPage}
                        employees={currentEmployees}
                        totalPages={Math.ceil(totalItems / entriesPerPage)}
                        onPageChange={setCurrentPage}
                        itemsPerPage={entriesPerPage}
                        totalItems={totalItems}
                        onEditEmployee={handleEditEmployee}
                        onDeleteEmployee={handleTerminateEmployee}
                    />
                ) : (
                    <TerminatedEmployeeTable
                        searchTerm={searchTerm}
                        entriesPerPage={entriesPerPage}
                        currentPage={currentPage}
                        employees={currentEmployees}
                        totalPages={Math.ceil(totalItems / entriesPerPage)}
                        onPageChange={setCurrentPage}
                        itemsPerPage={entriesPerPage}
                        totalItems={totalItems}
                        onReactivateEmployee={handleReactivateEmployee}
                        onDeleteEmployee={handleDeleteEmployee}
                    />
                )}
            </Card>
            {activeTab === 'employees' && (
                <EmployeeModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    mode={modalMode}
                    employee={selectedEmployee || undefined}
                    onSave={handleSaveEmployee}
                />
            )}
            <InviteModal
                isOpen={isInviteModalOpen}
                onClose={() => setIsInviteModalOpen(false)}
                groups={groups}
                onInviteSent={handleInviteSent}
            />
        </div>
    );
};

