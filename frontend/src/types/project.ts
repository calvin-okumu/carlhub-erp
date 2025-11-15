export interface ProjectFormData {
    name: string;
    client: number;
    status: 'active' | 'completed' | 'on-hold';
    priority: 'high' | 'medium' | 'low';
    start_date: string;
    end_date: string;
    budget?: string;
}