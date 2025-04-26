from django.core.management.base import BaseCommand
from django.utils.timezone import now
from users.models import CustomUser
from datetime import timedelta
from django.db import transaction


class Command(BaseCommand):
    help = 'Deactivate or delete users inactive for X months (default: 12)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--months', type=int, default=12,
            help='Number of months of inactivity before cleanup'
        )
        parser.add_argument(
            '--delete', action='store_true',
            help='Permanently delete users instead of just deactivating'
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        months = options['months']
        if months <= 0:
            raise ValueError("Months must be a positive integer")

        delete = options['delete']
        dry_run = options.get('dry-run', False)
        cutoff_date = now() - timedelta(days=30 * months)

        # Query inactive users, excluding superusers
        inactive_users = CustomUser.objects.filter(
            is_active=True,
            is_superuser=False,
            last_login__lt=cutoff_date
        ).exclude(last_login__isnull=True)

        count = inactive_users.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ No inactive users to clean up."))
            return

        if dry_run:
            self.stdout.write(f"Would {('delete' if delete else 'deactivate')} {count} user(s)")
            return

        try:
            with transaction.atomic():
                if delete:
                    # Log usernames or emails of deleted users for auditing
                    deleted_users = list(inactive_users.values_list('username', flat=True))
                    inactive_users.delete()
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ {count} user(s) permanently deleted for inactivity > {months} month(s)."
                    ))
                    self.stdout.write(f"Deleted users: {', '.join(deleted_users)}")
                else:
                    # Bulk update for deactivation
                    inactive_users.update(is_active=False)
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ {count} user(s) deactivated for inactivity > {months} month(s)."
                    ))

                # Log completion
                action = "deleted" if delete else "deactivated"
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Cleanup completed. Users {action}: {count}."
                ))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error during cleanup: {str(e)}")
            )
            raise


