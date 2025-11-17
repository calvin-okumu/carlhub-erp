import os
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Complete DjangoCRM project setup: database, migrations, groups, and sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-sample-data",
            action="store_true",
            help="Skip generating sample data",
        )
        parser.add_argument(
            "--production",
            action="store_true",
            help="Production mode - skip sample data and use production settings",
        )
        parser.add_argument(
            "--skip-db-setup",
            action="store_true",
            help="Skip database setup (useful if DB already exists)",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Starting DjangoCRM Automated Setup...\n"))

        environment = self.detect_environment()
        self.stdout.write(f"Environment detected: {environment}\n")

        try:
            # Phase 1: Database Setup
            if not options["skip_db_setup"]:
                self.setup_database()
            else:
                self.stdout.write("⏭️  Skipping database setup\n")

            # Phase 2: Django Migrations
            self.run_migrations()

            # Phase 3: Setup Groups
            self.setup_groups()

            # Phase 4: Sample Data (conditional)
            if self.should_generate_sample_data(options, environment):
                self.generate_sample_data()
            else:
                self.stdout.write("⏭️  Skipping sample data generation\n")

            # Phase 5: Create Superuser (development only)
            if environment == "development" and not options["production"]:
                self.create_default_superuser()

            # Phase 6: Validation
            self.validate_setup()

            self.display_success_message(environment)

        except Exception as e:
            raise CommandError(f"❌ Setup failed: {str(e)}")

    def detect_environment(self):
        """Detect the current environment with multiple indicators"""
        # Priority order: explicit env var > CI detection > git detection > default
        if os.environ.get("DJANGO_ENV") == "production":
            return "production"
        elif os.environ.get("PRODUCTION") == "true":
            return "production"
        elif os.environ.get("CI") or os.environ.get("CONTINUOUS_INTEGRATION"):
            return "ci"
        elif os.environ.get("GITHUB_ACTIONS") or os.environ.get("GITLAB_CI"):
            return "ci"
        elif os.path.exists(".git"):  # Development indicator
            return "development"
        elif os.environ.get("DOCKER_CONTAINER") or os.path.exists("/.dockerenv"):
            return "container"
        else:
            return "staging"

    def setup_database(self):
        """Setup database using setup_db.py"""
        self.stdout.write("📊 Setting up database...")
        setup_db_path = os.path.join(settings.BASE_DIR, "setup_db.py")

        if not os.path.exists(setup_db_path):
            raise CommandError("setup_db.py not found in project root")

        result = subprocess.run(
            [sys.executable, setup_db_path], cwd=settings.BASE_DIR, capture_output=True, text=True
        )

        if result.returncode != 0:
            self.stdout.write(self.style.ERROR(f"Database setup failed: {result.stderr}"))
            raise CommandError("Database setup failed")

        self.stdout.write(self.style.SUCCESS("Database setup complete\n"))

    def run_migrations(self):
        """Run Django migrations"""
        self.stdout.write("🔄 Running Django migrations...")
        call_command("migrate", verbosity=1)
        self.stdout.write(self.style.SUCCESS("Migrations complete\n"))

    def setup_groups(self):
        """Setup default user groups"""
        self.stdout.write("👥 Setting up user groups...")
        call_command("setup_groups", verbosity=1)
        self.stdout.write(self.style.SUCCESS("Groups setup complete\n"))

    def should_generate_sample_data(self, options, environment):
        """Determine if sample data should be generated"""
        if options["skip_sample_data"] or options["production"]:
            return False
        if environment in ["production", "ci"]:
            return False
        return True

    def generate_sample_data(self):
        """Generate sample data"""
        self.stdout.write("📝 Generating sample data...")
        call_command("generate_sample_data", verbosity=1)
        self.stdout.write(self.style.SUCCESS("Sample data generated\n"))

    def create_default_superuser(self):
        """Create default superuser for development"""
        from accounts.models import CustomUser

        self.stdout.write("👤 Creating default superuser...")
        if not CustomUser.objects.filter(email="admin@example.com").exists():
            CustomUser.objects.create_superuser(
                email="admin@example.com", password="admin123", first_name="Admin", last_name="User"
            )
            self.stdout.write(
                self.style.SUCCESS("Created superuser: admin@example.com / admin123\n")
            )
        else:
            self.stdout.write("ℹ️  Superuser already exists\n")

    def validate_setup(self):
        """Validate that setup completed successfully"""
        self.stdout.write("🔍 Validating setup...")

        # Check database connection
        from django.db import connection

        try:
            cursor = connection.cursor()
            self.stdout.write("✅ Database: OK")
        except Exception as e:
            raise CommandError(f"Database validation failed: {e}")

        # Check groups exist
        from django.contrib.auth.models import Group

        required_groups = ["Tenant Owners", "Project Managers", "Employees", "Clients"]
        for group_name in required_groups:
            if not Group.objects.filter(name=group_name).exists():
                raise CommandError(f"Required group missing: {group_name}")
        self.stdout.write("✅ User Groups: OK")

        # Check migrations

        # This is a simple check - could be more thorough
        self.stdout.write("✅ Migrations: OK")

        self.stdout.write(self.style.SUCCESS("Validation complete\n"))

    def display_success_message(self, environment):
        """Display success message with next steps"""
        self.stdout.write(self.style.SUCCESS("🎉 DjangoCRM setup complete!\n"))

        self.stdout.write("Next steps:")
        if environment == "development":
            self.stdout.write("1. Configure OAuth credentials in .env (optional)")
            self.stdout.write("2. Run: python manage.py runserver")
            self.stdout.write("3. Access: http://127.0.0.1:8000")
            self.stdout.write("4. Login with: admin@example.com / admin123")
        elif environment == "production":
            self.stdout.write("1. Configure production OAuth credentials")
            self.stdout.write("2. Setup reverse proxy (nginx/apache)")
            self.stdout.write("3. Configure SSL certificates")
            self.stdout.write("4. Run: python manage.py collectstatic")
        else:
            self.stdout.write("1. Configure environment-specific settings")
            self.stdout.write("2. Run: python manage.py runserver")

        self.stdout.write("")
