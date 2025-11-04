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
import { useEmployees } from "@/hooks/useEmployees";
import { getUsers } from "@/api/users";

export const UserSection = () => {
    const [activeTab, setActiveTab] = useState<'invites' | 'activeUsers' | 'employees'>('employees');
    const [employeeSubTab, setEmployeeSubTab] = useState<'active' | 'terminated'>('active');
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [selectedEmployee, setSelectedEmployee] = useState<any>(null);

    const { employees, loading, createEmployee, updateEmployee, deleteEmployee, refetch } = useEmployees();
    const [users, setUsers] = useState<any[]>([]);
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

    const handleTabChange = (tab: 'invites' | 'activeUsers' | 'employees') => {
        setActiveTab(tab);
        setCurrentPage(1);
        if (tab === 'employees') {
            setEmployeeSubTab('active');
        } else if (tab === 'activeUsers') {
            fetchUsers();
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

    const handleEditEmployee = (employee: any) => {
        setModalMode('edit');
        setSelectedEmployee(employee);
        setIsModalOpen(true);
    };

    const handleSaveEmployee = async (employeeData: any) => {
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

    const handleTerminateEmployee = async (employee: any) => {
        if (confirm(`Are you sure you want to terminate ${employee.first_name} ${employee.last_name}?`)) {
            try {
                await updateEmployee(employee.id, { is_active: false });
                refetch();
            } catch (error) {
                console.error('Error terminating employee:', error);
                alert('Failed to terminate employee');
            }
        }
    };

    const handleReactivateEmployee = async (employee: any) => {
        try {
            await updateEmployee(employee.id, { is_active: true });
            refetch();
        } catch (error) {
            console.error('Error reactivating employee:', error);
            alert('Failed to reactivate employee');
        }
    };

    const handleDeleteEmployee = async (employee: any) => {
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
                                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                                        employeeSubTab === 'active'
                                            ? 'bg-white text-blue-600 shadow-sm'
                                            : 'text-gray-600 hover:text-gray-900'
                                    }`}
                                >
                                    Active ({activeEmployees.length})
                                </button>
                                <button
                                    onClick={() => handleEmployeeSubTabChange('terminated')}
                                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                                        employeeSubTab === 'terminated'
                                            ? 'bg-white text-blue-600 shadow-sm'
                                            : 'text-gray-600 hover:text-gray-900'
                                    }`}
                                >
                                    Terminated ({terminatedEmployees.length})
                                </button>
                            </div>
                        </div>
                    )}
                    <div className="flex items-center space-x-4">
                        <Input
                            placeholder={`Search ${activeTab === 'invites' ? 'invites' : activeTab === 'activeUsers' ? 'users' : employeeSubTab === 'active' ? 'active employees' : 'terminated employees'}`}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <Select>
                            <option value="export">Export</option>
                        </Select>
                    </div>
                </div>
                  {(loading || usersLoading) ? (
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
                          users={users}
                          totalPages={Math.ceil(users.length / entriesPerPage)}
                          onPageChange={setCurrentPage}
                          itemsPerPage={entriesPerPage}
                          totalItems={users.length}
                      />
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
                      employee={selectedEmployee}
                      onSave={handleSaveEmployee}
                  />
              )}
         </div>
     );
};

