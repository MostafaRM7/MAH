import os
import glob
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Removes all migration files except __init__.py in each app's migrations directory."

    def handle(self, *args, **options):
        deleted_files = 0

        for app_config in apps.get_app_configs():
            migration_dir = os.path.join(app_config.path, "migrations")

            if os.path.exists(migration_dir) and os.path.isdir(migration_dir):
                migration_files = glob.glob(os.path.join(migration_dir, "*.py"))
                migration_files += glob.glob(os.path.join(migration_dir, "*.pyc"))

                for file in migration_files:
                    if os.path.basename(file) != "__init__.py":
                        os.remove(file)
                        self.stdout.write(self.style.SUCCESS(f"Deleted: {file}"))
                        deleted_files += 1

        if deleted_files == 0:
            self.stdout.write(self.style.WARNING("No migration files found to delete."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Migration cleanup complete. {deleted_files} files deleted."))