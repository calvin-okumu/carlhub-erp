from django.core.management.base import BaseCommand, CommandError

from project.models import Client
from ticketing.models import ClientIntegration


class Command(BaseCommand):
    help = "Generate or rotate a client API key for ticketing inbound requests."

    def add_arguments(self, parser):
        parser.add_argument("--client-id", type=str, help="Client UUID")
        parser.add_argument("--client-slug", type=str, help="Client slug")
        parser.add_argument(
            "--rotate",
            action="store_true",
            help="Rotate existing API key if integration already exists",
        )

    def handle(self, *args, **options):
        client_id = options.get("client_id")
        client_slug = options.get("client_slug")

        if not client_id and not client_slug:
            raise CommandError("Provide --client-id or --client-slug.")

        if client_id and client_slug:
            raise CommandError("Provide only one of --client-id or --client-slug.")

        try:
            if client_id:
                client = Client.objects.get(id=client_id)
            else:
                client = Client.objects.get(slug=client_slug)
        except Client.DoesNotExist as exc:
            raise CommandError("Client not found.") from exc

        integration = getattr(client, "integration", None)
        if integration and not options.get("rotate"):
            raise CommandError(
                "Integration already exists. Use --rotate to regenerate the API key."
            )

        raw_key = ClientIntegration.generate_raw_key()
        if integration:
            integration.set_key(raw_key)
            integration.save(update_fields=["api_key_prefix", "api_key_hash"])
        else:
            integration = ClientIntegration(client=client)
            integration.set_key(raw_key)
            integration.save()

        self.stdout.write(self.style.SUCCESS("Client API key generated."))
        self.stdout.write(f"client_id={client.id}")
        self.stdout.write(f"api_key={raw_key}")
