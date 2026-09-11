import os
import django


def fix_inconsistent_history():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    from django.db import connection
    from django.utils import timezone

    try:
        tables = connection.introspection.table_names()
        if 'django_migrations' not in tables:
            return

        with connection.cursor() as cursor:
            # Check master_data 0001_initial
            cursor.execute("SELECT id FROM django_migrations WHERE app = 'master_data' AND name = '0001_initial'")
            md = cursor.fetchone()

            # Check apps that depend on master_data.0001_initial
            dependent_apps = ['finance', 'products', 'production', 'sales', 'purchasing', 'warehouse']
            needs_master_data = False
            for app_name in dependent_apps:
                cursor.execute("SELECT id FROM django_migrations WHERE app = %s AND name = '0001_initial'", [app_name])
                if cursor.fetchone():
                    needs_master_data = True
                    break

            if needs_master_data and not md:
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    ['master_data', '0001_initial', timezone.now()]
                )
                print("[Auto-Fix] Injected master_data.0001_initial into django_migrations to resolve InconsistentMigrationHistory.")

    except Exception as e:
        print(f"[Auto-Fix] Non-fatal migration history pre-check: {e}")


if __name__ == '__main__':
    fix_inconsistent_history()
