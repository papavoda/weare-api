import os
import sys
from django.core.management.commands.runserver import Command as BaseCommand

class Command(BaseCommand):
    def run(self, *args, **options):
        from uvicorn.main import run
        run(["config.asgi:application", "--reload"])

