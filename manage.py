#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def auto_fix_inconsistent_migrations():
    """Auto-reconciles ghost migrations and missing migration dependencies before migrate runs."""
    if len(sys.argv) > 1 and sys.argv[1] in ('migrate', 'showmigrations'):
        try:
            import django
            django.setup()
            from django.db import connection
            from django.utils import timezone
            from django.db.migrations.loader import MigrationLoader

            tables = set(connection.introspection.table_names())
            if 'django_migrations' in tables:
                with connection.cursor() as cursor:
                    # If core 'users' table does not physically exist, all migrations must be re-applied from scratch
                    if 'users' not in tables:
                        cursor.execute("DELETE FROM django_migrations;")
                        print("[Auto-Fix] 'users' table missing. Reset django_migrations history to allow full initial schema creation.")
                    else:
                        # Validate individual apps whose initial tables might be missing
                        app_table_map = {
                            'accounts': 'users',
                            'master_data': 'company_profile',
                            'finance': 'financial_transactions',
                            'products': 'products',
                            'production': 'production_orders',
                            'sales': 'sales',
                            'purchasing': 'purchases',
                            'warehouse': 'warehouses',
                            'audit': 'audit_logs',
                        }
                        for app_name, table_name in app_table_map.items():
                            if table_name not in tables:
                                cursor.execute("DELETE FROM django_migrations WHERE app = %s", [app_name])
                                print(f"[Auto-Fix] Table '{table_name}' missing. Removed '{app_name}' from django_migrations.")

                # Re-load graph to check for missing parent dependencies
                loader = MigrationLoader(connection, ignore_no_migrations=True)
                applied = set(loader.applied_migrations.keys())

                with connection.cursor() as cursor:
                    for (app, name), node in loader.graph.nodes.items():
                        if (app, name) in applied:
                            for parent in node.dependencies:
                                if parent in loader.graph.nodes and parent not in applied:
                                    cursor.execute(
                                        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                                        [parent[0], parent[1], timezone.now()]
                                    )
                                    applied.add(parent)
                                    print(f"[Auto-Fix] Injected missing migration parent {parent[0]}.{parent[1]} into django_migrations.")
        except Exception as e:
            # Non-blocking if database is offline or uninitialized
            print(f"[Auto-Fix Warning] {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    auto_fix_inconsistent_migrations()
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
