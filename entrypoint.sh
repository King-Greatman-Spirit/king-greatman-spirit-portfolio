#!/bin/sh
# Runs inside the container on every start.
# 1. Apply migrations
# 2. Load KGS.json fixture ONLY when the database is empty (first boot)
# 3. Collect static files
# 4. Start gunicorn
set -e

echo "[entrypoint] applying migrations..."
python manage.py migrate --noinput

echo "[entrypoint] checking whether the database needs the KGS.json fixture..."
if python - <<'PY'
import os, sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KingGreatmanSpirit.settings")
django.setup()

from accounts.models import Account

if Account.objects.count() == 0:
    print("[entrypoint] database is empty -> loading KGS.json")
    sys.exit(0)
print("[entrypoint] database already has data -> skipping fixture load")
sys.exit(1)
PY
then
  echo "[entrypoint] loading KGS.json fixture..."
  python manage.py loaddata KGS.json --traceback
else
  echo "[entrypoint] fixture load not needed."
fi

echo "[entrypoint] collecting static files..."
python manage.py collectstatic --noinput

echo "[entrypoint] starting gunicorn..."
exec gunicorn KingGreatmanSpirit.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120