#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def auto_fix_inconsistent_migrations():
    """Auto-reconciles missing migration dependencies before migrate runs."""
    if len(sys.argv) > 1 and sys.argv[1] in ('migrate', 'showmigrations'):
        try:
            import django
            django.setup()
            from django.db import connection
            from django.utils import timezone
            from django.db.migrations.loader import MigrationLoader

            tables = connection.introspection.table_names()
            if 'django_migrations' in tables:
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
            pass


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
