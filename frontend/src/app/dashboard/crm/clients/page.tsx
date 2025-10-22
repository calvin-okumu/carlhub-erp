 import ClientSection from '@/components/dashboard/crm/clients/ClientSection';

export default function ClientsPage() {
    return (
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <h1 className="h1-title">Clients</h1>
            <ClientSection />
        </div>
    );
}
