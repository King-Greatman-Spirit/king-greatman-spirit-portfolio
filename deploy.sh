#!/bin/bash
# ============================================================
# KGS AUTO-DEPLOY - Docker + PostgreSQL
# Safe to run over and over (idempotent). Run as root or sudo:
#   bash deploy.sh
# ============================================================
set -e

APP=/var/www/kinggreatmanspirit
cd "$APP" || { echo "!! $APP not found - clone the repo here first"; exit 1; }

echo "==> [1/7] Fix git ownership + pull latest code"
git config --global --add safe.directory "$APP"
git pull

echo "==> [2/7] Install Docker if missing"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

echo "==> [3/7] Stop old systemd service if it still exists"
if systemctl list-unit-files 2>/dev/null | grep -q '^kinggreatmanspirit'; then
  systemctl stop kinggreatmanspirit 2>/dev/null || true
  systemctl disable kinggreatmanspirit 2>/dev/null || true
  echo "old service stopped + disabled"
fi

echo "==> [4/7] Ensure .env exists"
if [ ! -f .env ]; then
  echo "!! .env MISSING - creating a minimal one with a fresh SECRET_KEY."
  echo "!! You MUST add your payment + email keys now:  nano .env"
  NEWKEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
  cat > .env <<EOF
SECRET_KEY=$NEWKEY
DEBUG=False
ALLOWED_HOSTS=kinggreatmanspirit.com,www.kinggreatmanspirit.com,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://kinggreatmanspirit.com,https://www.kinggreatmanspirit.com
SITE_URL=https://kinggreatmanspirit.com
TIME_ZONE=UTC
DB_ENGINE=django.db.backends.postgresql
DB_NAME=kgs_db
DB_USER=kgs_user
DB_PASSWORD=kgs_password
DB_HOST=db
DB_PORT=5432
EOF
  echo "!! Edit .env then re-run: bash deploy.sh"
  exit 1
else
  echo ".env exists - ok"
fi

echo "==> [5/7] Build & start (migrate + KGS.json + collectstatic + gunicorn happen inside)"
docker compose up -d --build

echo "==> [6/7] Point nginx at Docker (127.0.0.1:8000)"
NGINX_CONF=/etc/nginx/sites-available/kinggreatmanspirit
if [ -f "$NGINX_CONF" ] && grep -q "unix:/run/gunicorn" "$NGINX_CONF"; then
  sed -i 's|proxy_pass http://unix:/run/gunicorn/kinggreatmanspirit.sock;|proxy_pass http://127.0.0.1:8000;|' "$NGINX_CONF"
  echo "nginx proxy fixed (127.0.0.1:8000)"
fi
nginx -t && systemctl reload nginx

echo "==> [7/7] Verify"
sleep 5
curl -s -o /dev/null -w "https://kinggreatmanspirit.com -> %{http_code}\n" https://kinggreatmanspirit.com || true
docker compose logs web 2>/dev/null | grep -i "installed" || echo "(no fresh fixture load - DB already has data, expected)"

echo "==> DEPLOY DONE. Open https://kinggreatmanspirit.com"