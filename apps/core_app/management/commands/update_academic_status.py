from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core_app.models import UserProfile


class Command(BaseCommand):
    help = 'Update is_academic_ja flag for all existing users based on their email addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        updated_count = 0
        japanese_academic_count = 0
        
        # Get all user profiles
        profiles = UserProfile.objects.select_related('user')
        
        for profile in profiles:
            old_status = profile.is_academic_ja
            
            # Update academic status (this will be calculated based on email)
            new_status = profile.update_academic_status()
            
            if old_status != new_status:
                if not dry_run:
                    profile.save()
                updated_count += 1
                
                if new_status:
                    japanese_academic_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ {profile.user.email} -> Japanese Academic Institution'
                        )
                    )
                else:
                    self.stdout.write(
                        f'  {profile.user.email} -> General User'
                    )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total profiles processed: {profiles.count()}')
        self.stdout.write(f'Profiles updated: {updated_count}')
        self.stdout.write(
            self.style.SUCCESS(
                f'Japanese academic institutions: {japanese_academic_count}'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nThis was a dry run. Use --dry-run=false to apply changes.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ Academic status updated successfully!'
                )
            )