from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    help = 'Waits for the database to become available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        # Loop until database is ready
        while not db_conn:
            try:
                db_conn = connections['default']
                # Try to get a cursor to test connection
                db_conn.cursor()
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is available!'))