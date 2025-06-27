from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from apps.monitoring_app.models import SystemMetric, ErrorLog, APIUsageMetric, UserActivity


class Command(BaseCommand):
    help = 'Generate sample monitoring data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours of data to generate (default: 24)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing monitoring data before generating new data',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        
        if options['clear']:
            self.stdout.write('Clearing existing monitoring data...')
            SystemMetric.objects.all().delete()
            ErrorLog.objects.all().delete()
            APIUsageMetric.objects.all().delete()
            UserActivity.objects.all().delete()
        
        self.stdout.write(f'Generating {hours} hours of monitoring data...')
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='monitoring_test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Generate data for each hour
        for hour in range(hours):
            timestamp_base = timezone.now() - timedelta(hours=hour)
            
            # Generate system metrics (response times)
            endpoints = [
                '/scholar/', '/writer/', '/viz/', '/code/', '/core/dashboard/',
                '/api/v1/profile/me/', '/api/v1/documents/', '/api/v1/projects/'
            ]
            
            for _ in range(random.randint(10, 50)):  # 10-50 requests per hour
                endpoint = random.choice(endpoints)
                response_time = random.normalvariate(200, 100)  # Normal distribution around 200ms
                response_time = max(50, response_time)  # Min 50ms
                
                status_codes = [200] * 85 + [404] * 8 + [500] * 4 + [403] * 3  # Weighted distribution
                status_code = random.choice(status_codes)
                
                timestamp = timestamp_base + timedelta(minutes=random.randint(0, 59))
                
                SystemMetric.objects.create(
                    metric_type='response_time',
                    endpoint=endpoint,
                    value=response_time,
                    status_code=status_code,
                    user=user if random.random() > 0.3 else None,  # 70% authenticated requests
                    timestamp=timestamp,
                    metadata={
                        'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                        'user_agent': 'Mozilla/5.0 (Test Browser)',
                        'ip_address': f'192.168.1.{random.randint(1, 255)}'
                    }
                )
            
            # Generate API usage metrics
            apis = ['semantic_scholar', 'arxiv', 'pubmed', 'doaj', 'biorxiv']
            for _ in range(random.randint(5, 20)):  # 5-20 API calls per hour
                api_name = random.choice(apis)
                api_response_time = random.normalvariate(800, 300)  # APIs are slower
                api_response_time = max(100, api_response_time)
                
                success = random.random() > 0.05  # 95% success rate
                status_code = 200 if success else random.choice([429, 500, 503])
                
                timestamp = timestamp_base + timedelta(minutes=random.randint(0, 59))
                
                APIUsageMetric.objects.create(
                    api_name=api_name,
                    endpoint=f'https://api.{api_name}.org/search',
                    response_time=api_response_time,
                    status_code=status_code,
                    success=success,
                    query_params={'q': 'machine learning', 'limit': 10},
                    response_size=random.randint(1000, 50000),
                    timestamp=timestamp
                )
            
            # Generate user activities
            activities = ['login', 'search', 'document_create', 'document_edit', 'project_create']
            for _ in range(random.randint(3, 15)):  # 3-15 user activities per hour
                activity_type = random.choice(activities)
                timestamp = timestamp_base + timedelta(minutes=random.randint(0, 59))
                
                UserActivity.objects.create(
                    user=user,
                    activity_type=activity_type,
                    details={
                        'path': f'/test/{activity_type}/',
                        'success': True
                    },
                    session_id=f'session_{random.randint(1000, 9999)}',
                    ip_address=f'192.168.1.{random.randint(1, 255)}',
                    user_agent='Mozilla/5.0 (Test Browser)',
                    timestamp=timestamp
                )
            
            # Generate some errors (less frequent)
            if random.random() < 0.3:  # 30% chance of error each hour
                error_types = ['AttributeError', 'KeyError', 'ValueError', 'TimeoutError', 'ConnectionError']
                severity_levels = ['low'] * 5 + ['medium'] * 3 + ['high'] * 2 + ['critical']
                
                timestamp = timestamp_base + timedelta(minutes=random.randint(0, 59))
                
                ErrorLog.objects.create(
                    severity=random.choice(severity_levels),
                    error_type=random.choice(error_types),
                    message=f'Sample error message for testing: {random.randint(1, 1000)}',
                    stack_trace='Traceback (most recent call last):\n  File "test.py", line 1, in <module>\n    sample error',
                    endpoint=random.choice(endpoints),
                    user=user if random.random() > 0.5 else None,
                    user_agent='Mozilla/5.0 (Test Browser)',
                    ip_address=f'192.168.1.{random.randint(1, 255)}',
                    timestamp=timestamp,
                    resolved=random.random() > 0.7  # 30% resolved
                )
        
        # Print summary
        total_metrics = SystemMetric.objects.count()
        total_api_calls = APIUsageMetric.objects.count()
        total_activities = UserActivity.objects.count()
        total_errors = ErrorLog.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated:\n'
                f'  - {total_metrics} system metrics\n'
                f'  - {total_api_calls} API usage records\n'
                f'  - {total_activities} user activities\n'
                f'  - {total_errors} error logs'
            )
        )