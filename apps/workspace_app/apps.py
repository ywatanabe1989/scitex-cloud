from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class WorkspaceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.workspace_app'
    verbose_name = 'SciTeX Workspace Application'

    def ready(self):
        # Import signals to ensure they are connected
        import apps.workspace_app.signals
        
        # Auto-create cache table if using database cache
        self.ensure_cache_table()

    def ensure_cache_table(self):
        """Ensure cache table exists for database cache."""
        try:
            # Check if we're using database cache
            cache_config = getattr(settings, 'CACHES', {}).get('default', {})
            if cache_config.get('BACKEND') == 'django.core.cache.backends.db.DatabaseCache':
                from django.core.management import call_command
                from django.db import connection
                
                table_name = cache_config.get('LOCATION', 'cache_table')
                
                with connection.cursor() as cursor:
                    # Check if cache table exists (SQLite specific query)
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                        [table_name]
                    )
                    if not cursor.fetchone():
                        logger.info(f"Cache table '{table_name}' not found, creating...")
                        call_command('createcachetable', table_name)
                        logger.info(f"✅ Cache table '{table_name}' created successfully")
                    else:
                        logger.debug(f"Cache table '{table_name}' already exists")
                        
        except Exception as e:
            logger.warning(f"Could not ensure cache table: {e}")