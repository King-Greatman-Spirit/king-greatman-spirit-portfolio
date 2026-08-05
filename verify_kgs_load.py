import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KingGreatmanSpirit.settings")
django.setup()

from django.conf import settings
from django.core.management import call_command

settings.DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}

call_command("migrate", verbosity=0)
call_command("loaddata", "KGS.json", verbosity=0)
print("KGS.json LOADED CLEANLY into a fresh database")
