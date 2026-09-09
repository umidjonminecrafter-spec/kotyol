import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Auto-migrate database on application startup (guarantees tables exist on Render/production)
if os.getenv('AUTO_MIGRATE', 'true').lower() in ('1', 'true', 'yes'):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        print("[Kotyol ERP] Auto-migration completed successfully.")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"[Kotyol ERP] Auto-migration failed on startup: {e}", exc_info=True)
        print(f"[Kotyol ERP] Auto-migration error: {e}")
