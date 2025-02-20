import glob
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Removes all migration files (except __init__.py) from the project.'

    def handle(self, *args, **options):
        project_root = os.getcwd()  # This assumes you are running manage.py from the project root
        deleted_files = 0

        for root, dirs, files in os.walk(project_root):
            if 'migrations' in dirs:
                migration_path = os.path.join(root, 'migrations')
                self.stdout.write(f'Processing migrations in: {migration_path}')

                # Delete all Python migration files except __init__.py
                for file in glob.glob(os.path.join(migration_path, "*.py")):
                    if not file.endswith("__init__.py"):
                        os.remove(file)
                        deleted_files += 1
                        self.stdout.write(f"Deleted: {file}")

                # Optionally remove the __pycache__ folder if it exists
                pycache_path = os.path.join(migration_path, '__pycache__')
                if os.path.exists(pycache_path):
                    for file in glob.glob(os.path.join(pycache_path, "*.pyc")):
                        os.remove(file)
                        self.stdout.write(f"Deleted: {file}")
                    os.rmdir(pycache_path)
                    self.stdout.write(f"Deleted directory: {pycache_path}")

        self.stdout.write(self.style.SUCCESS(f"Completed! Total files deleted: {deleted_files}"))
