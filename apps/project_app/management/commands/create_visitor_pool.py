"""
Management command to create visitor pool.

Usage:
    python manage.py create_visitor_pool                # Create 32 visitors (default)
    python manage.py create_visitor_pool --size 16      # Create 16 visitors
    python manage.py create_visitor_pool --status       # Show pool status
"""

from django.core.management.base import BaseCommand
from apps.project_app.services.visitor_pool import VisitorPool


class Command(BaseCommand):
    help = "Create and manage visitor pool (visitor-001 to visitor-032)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--size",
            type=int,
            default=None,
            help="Pool size (default: 32)",
        )
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show pool status without creating",
        )

    def handle(self, *args, **options):
        if options["status"]:
            # Show pool status
            status = VisitorPool.get_pool_status()
            self.stdout.write("\n=== Visitor Pool Status ===")
            self.stdout.write(f"Total slots: {status['total']}")
            self.stdout.write(f"Allocated: {status['allocated']}")
            self.stdout.write(f"Free: {status['free']}")
            self.stdout.write(f"Expired: {status['expired']}")
            return

        # Create visitor pool
        pool_size = options["size"] or VisitorPool.POOL_SIZE

        self.stdout.write(f"\nInitializing visitor pool (size={pool_size})...")
        self.stdout.write("This will create:")
        self.stdout.write(f"  - visitor-001 to visitor-{pool_size:03d} (users)")
        self.stdout.write(
            f'  - {pool_size} "default-project" projects (one per visitor user)'
        )
        self.stdout.write("")

        created = VisitorPool.initialize_pool(pool_size=pool_size)

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Created {created} visitor accounts with projects")
        )
        self.stdout.write("\nPool ready for visitors!")
        self.stdout.write(
            f"\nTo check status: python manage.py create_visitor_pool --status"
        )
