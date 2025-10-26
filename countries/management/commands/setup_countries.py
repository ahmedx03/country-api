import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup initial directories'
    
    def handle(self, *args, **options):
        os.makedirs(settings.CACHE_DIR, exist_ok=True)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        self.stdout.write(
            self.style.SUCCESS('Successfully created cache and media directories')
        )