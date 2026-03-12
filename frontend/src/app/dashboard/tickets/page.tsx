import TicketSection from "@/components/dashboard/tickets/TicketSection";

export default function TicketsPage() {
  return (
    <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="h1-title">Tickets</h1>
      <TicketSection />
    </div>
  );
}
