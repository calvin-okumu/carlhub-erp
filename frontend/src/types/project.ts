export interface ProjectFormData {
    name: string;
    client: string;
    status: 'active' | 'completed' | 'on-hold';
    priority: 'high' | 'medium' | 'low';
    start_date: string;
    end_date: string;
    budget?: string;
}