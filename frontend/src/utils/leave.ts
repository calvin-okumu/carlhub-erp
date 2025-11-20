export const formatLeaveType = (type: string): string => {
    const typeMap: Record<string, string> = {
        annual: 'Annual Leave',
        sick: 'Sick Leave',
        casual: 'Casual Leave',
        maternity: 'Maternity Leave',
        paternity: 'Paternity Leave',
        unpaid: 'Unpaid Leave',
    };
    return typeMap[type] ?? type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const formatDaysAllowed = (days: number): string => {
    return `${days} days/year`;
};

export const formatMaxAtOnce = (days: number): string => {
    return days > 0 ? `${days} days` : 'No limit';
};

export const formatAdvanceNotice = (days: number): string => {
    return days > 0 ? `${days} days` : 'Same day';
};