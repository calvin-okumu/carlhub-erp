export interface ProjectFormData {
    name: string;
    client: string;
    status: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived';
    priority: 'high' | 'medium' | 'low';
    start_date: string;
    end_date: string;
    budget?: string;
}
