#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# build.sh — Render build script
# Runs once per deploy BEFORE the app starts
# ═══════════════════════════════════════════════════════════════

# Exit immediately if any command fails
# WHY: Without this, a failed pip install would be silently ignored
# and the deploy would continue with a broken environment
set -o errexit

# ── 1. Install Python dependencies ───────────────────────────
echo "→ Installing production dependencies..."
pip install -r requirements/production.txt

# ── 2. Collect static files ──────────────────────────────────
# Copies everything from your apps' static/ folders and
# STATICFILES_DIRS into STATIC_ROOT (staticfiles/)
# WhiteNoise serves from STATIC_ROOT in production
echo "→ Collecting static files..."
python manage.py collectstatic --no-input
# --no-input skips the "Are you sure?" prompt in CI

# ── 3. Run database migrations ───────────────────────────────
# Apply any new migrations — keeps DB schema in sync with models
echo "→ Running database migrations..."
python manage.py migrate --no-input

# ── 4. Create Admin Superuser (Free Instance Workaround) ─────
# Automatically hooks into your Render environment panel variables
# The '|| true' ensures subsequent deploys don't crash when user exists
echo "→ Checking/Creating admin superuser..."
python manage.py createsuperuser --no-input || true

echo "✓ Build complete"
