import os
import sys
import django


def fix_inconsistent_history():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    from django.db import connection
    from django.utils import timezone
    from django.db.migrations.loader import MigrationLoader

    try:
        tables = set(connection.introspection.table_names())
        if 'django_migrations' not in tables:
            return

        with connection.cursor() as cursor:
            if 'users' not in tables:
                cursor.execute("DELETE FROM django_migrations;")
                print("[Auto-Fix] 'users' table missing. Reset django_migrations history to allow full initial schema creation.")
            else:
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
        print(f"[Auto-Fix Warning] {e}")


if __name__ == '__main__':
    fix_inconsistent_history()
