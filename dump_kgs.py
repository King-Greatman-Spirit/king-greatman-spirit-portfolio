import io
import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KingGreatmanSpirit.settings")
django.setup()

from django.core.management import call_command

APPS = ["about", "resume", "portfolio", "service", "contact", "accounts", "payments", "dashboard"]
OUT = "KGS.json"

buf = io.StringIO()
call_command("dumpdata", *APPS, indent=2, stdout=buf)

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(buf.getvalue())

with open(OUT, encoding="utf-8") as f:
    records = json.load(f)

print(f"WROTE {OUT}: {len(buf.getvalue()):,} chars | {len(records):,} records | UTF-8")
