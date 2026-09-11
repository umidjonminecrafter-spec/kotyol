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

        loader = MigrationLoader(connection, ignore_no_migrations=True)
        applied = set(loader.applied_migrations.keys())

        with connection.cursor() as cursor:
            if 'auth_permission' in tables or 'django_content_type' in tables:
                django_builtins = {'contenttypes', 'auth', 'admin', 'sessions'}
                for (app, name) in list(loader.graph.nodes.keys()):
                    if app in django_builtins and (app, name) not in applied:
                        cursor.execute(
                            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                            [app, name, timezone.now()]
                        )
                        applied.add((app, name))
                        print(f"[Auto-Fix] Pre-existing table detected. Marked built-in {app}.{name} as applied.")

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
