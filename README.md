# TheSolitaryLand — Photography Portfolio

A cinematic personal brand website and Django-powered CMS for managing
photography, video, and visual storytelling work — with a full REST API
alongside the public site.

**Tech stack:** Python · Django 6.0.6 · PostgreSQL · Django REST Framework · Cloudinary · Bootstrap 5

---

## Project Vision

Personal brand platform for TheSolitaryLand — Photographer · Visual Storyteller · Builder of Visual Systems.

Built to showcase photography and video work through a cinematic,
minimal "luxury editorial dark" frontend, while demonstrating
production-grade Django backend engineering: a clean MVT layer, a
versioned REST API, automated tests, and a deployed production
configuration.

---

## Features

**User-facing**
- Cinematic hero and editorial dark aesthetic (Cormorant Garamond + DM Sans)
- Photography gallery with category/tag filtering and masonry layout
- Photo detail pages with story, location metadata, and camera info
- Video portfolio supporting self-hosted MP4 uploads and YouTube/Vimeo embeds
- Curated album series (ordered photo collections)
- Featured-work sections for the homepage
- About page and contact form

**Backend CMS (Django Admin)**
- Upload and manage photos, videos, and albums
- Category and tag assignment
- Featured content control, with configurable display order
- Contact message inbox with read/unread status

**REST API** (`/api/v1/`)
- Full read-only API for photos, videos, albums, categories, and tags
- Write endpoint for contact form submissions
- Filtering, search, and ordering on list endpoints (django-filter)
- Pagination (50 items/page)
- Anonymous request throttling
- CORS support for external/frontend consumers
- Interactive docs via drf-spectacular (Swagger UI + ReDoc)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | Django 6.0.6 |
| API | Django REST Framework 3.17 · django-filter · drf-spectacular |
| Database | PostgreSQL |
| Frontend | HTML · CSS (Bootstrap 5) · JavaScript |
| Media storage | Cloudinary (production) · local filesystem (development) |
| Static files | WhiteNoise (compressed, manifest-hashed) |
| Deployment | Render (Gunicorn, PostgreSQL) |

---

## Local Development Setup

**Prerequisites:** Python 3.14+, PostgreSQL

```bash
# 1. Clone the repo
git clone https://github.com/jh11solitude/thesolitaryland-portfolio.git
cd thesolitaryland-portfolio

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies (local/dev extras included)
pip install -r requirements/local.txt

# 4. Create the PostgreSQL database
createdb thesolitaryland_portfolio

# 5. Configure environment variables
# Create a .env file in the project root with at least:
#   SECRET_KEY=your-dev-secret-key
#   DB_NAME=thesolitaryland_portfolio
#   DB_USER=postgres
#   DB_PASSWORD=
#   DB_HOST=localhost
#   DB_PORT=5432
DJANGO_SETTINGS_MODULE=config.settings.local

# 6. Run migrations
python manage.py migrate

# 7. Create an admin user
python manage.py createsuperuser

# 8. Start the development server
python manage.py runserver
```

Visit:
- `http://127.0.0.1:8000` — public site
- `http://127.0.0.1:8000/admin` — CMS / Django Admin
- `http://127.0.0.1:8000/api/v1/` — API root
- `http://127.0.0.1:8000/api/v1/docs/` — Swagger UI
- `http://127.0.0.1:8000/api/v1/redoc/` — ReDoc

---

## Project Structure

```
thesolitaryland-portfolio/
├── apps/
│   ├── portfolio/         # Photo, Video, Album, Category, Tag, FeaturedWork
│   ├── pages/              # Home and About views
│   ├── contact/            # Contact form (MVT) and ContactMessage storage
│   └── api/                 # Versioned REST API (serializers, filters, views, tests)
├── config/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── local.py        # Development (debug toolbar, local DB)
│   │   └── production.py   # Render deployment (WhiteNoise, Cloudinary, security headers)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/               # HTML templates (base, portfolio, pages, contact)
├── static/                  # CSS, JS, images
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── build.sh                  # Render build script (install, collectstatic, migrate, superuser)
├── Procfile                   # Gunicorn start command
├── runtime.txt                 # Python version pin
├── render-env-vars.example.txt # Documented list of required Render env vars
└── manage.py
```

---

## Database Design

Eight models across two apps:

**`apps.portfolio`** — `Category` · `Tag` · `Photo` · `Video` · `Album` · `AlbumPhoto` (through-table) · `FeaturedWork`
**`apps.contact`** — `ContactMessage`

Notable design details:
- Auto-generated, unique slugs on `Category`, `Tag`, `Photo`, `Video`, and `Album` (SEO-friendly URLs, no numeric IDs in routes)
- `AlbumPhoto` is an explicit through-table carrying photo ordering within an album
- `FeaturedWork` uses a generic pattern (`get_item()` + `clean()` validation) to feature either a `Photo` or a `Video` from a single model, with a display-order field
- `Photo` stores structured shoot metadata (location, camera/lens/settings string, date taken) alongside the image itself

---

## REST API

Base path: `/api/v1/`

| Endpoint | Description |
|---|---|
| `GET /api/v1/` | API root — lists available resources |
| `GET /api/v1/photos/` | List photos (filterable, searchable, orderable) |
| `GET /api/v1/photos/featured/` | Featured photos |
| `GET /api/v1/photos/<slug>/` | Photo detail |
| `GET /api/v1/videos/` | List videos |
| `GET /api/v1/videos/<slug>/` | Video detail |
| `GET /api/v1/albums/` | List albums |
| `GET /api/v1/albums/<slug>/` | Album detail (with ordered photos) |
| `GET /api/v1/categories/` | List categories |
| `GET /api/v1/tags/` | List tags |
| `POST /api/v1/contact/` | Submit a contact message |
| `GET /api/v1/schema/` | Raw OpenAPI schema |
| `GET /api/v1/docs/` | Swagger UI |
| `GET /api/v1/redoc/` | ReDoc |

Design notes:
- Fixed URL ordering (e.g. `photos/featured/` registered before `photos/<slug:slug>/`) so literal paths aren't swallowed by the slug pattern
- List endpoints are paginated at 50 items/page and support `?category=`, `?tag=`, search, and ordering query params
- Anonymous requests are throttled (200/hour by default) to protect the public API from abuse
- Business logic shared between the MVT views and the API (e.g. featured-item queries) lives in a common `managers.py` service layer to avoid duplication

---

## Testing

Run the test suite with:

```bash
python manage.py test
```

The API layer (`apps/api/tests.py`) has full coverage of photo, video, contact, and taxonomy endpoints, plus the API root — 24 tests in total, covering list/detail responses, filtering, and the contact submission flow.

---

## Deployment

Deployed on **Render** as a Gunicorn web service with a managed PostgreSQL database.

- `build.sh` runs on every deploy: installs production dependencies, runs `collectstatic`, applies migrations, and ensures the admin superuser exists (idempotent — safe on redeploys)
- `Procfile` starts the app with `gunicorn config.wsgi:application`
- Static files are served by **WhiteNoise** with compressed, content-hashed filenames for long-term caching
- Media uploads (photos, videos, thumbnails) are stored on **Cloudinary** in production via Django's unified `STORAGES` setting (Django 5.1+ replaced the old `STATICFILES_STORAGE` / `DEFAULT_FILE_STORAGE` settings, which are silently ignored on Django 6.0)
- Security hardening in `production.py`: forced HTTPS/HSTS, secure cookies, `X-Frame-Options: DENY`, and proxy SSL header support behind Render's load balancer
- See `render-env-vars.example.txt` for the full list of environment variables required on Render (secret key, database URL, allowed hosts, email/SMTP, CORS/CSRF origins, Cloudinary credentials, and superuser bootstrap credentials)

---

## Skills Demonstrated

This project covers skills from the **Meta Back-End Developer Professional Certificate**, applied at production scope:

- Django models, ORM relationships (FK, M2M through-tables), migrations
- Class-based views (ListView, DetailView, TemplateView) and a shared service layer
- Django Admin customisation
- PostgreSQL integration, connection pooling in production
- REST API design with Django REST Framework — filtering, pagination, throttling, auto-generated OpenAPI docs
- Automated testing (`APITestCase`)
- Git feature-branch workflow with Conventional Commits
- Environment-split settings (`base` / `local` / `production`) and production deployment configuration (Gunicorn, WhiteNoise, Cloudinary, security headers)

---

## Development Phases

- [x] Phase 1 — System blueprint and architecture design
- [x] Phase 2 — Database design and Django models
- [x] Phase 3 — Project setup, settings, Admin
- [x] Phase 4 — Git workflow and repository structure
- [x] Phase 5 — Feature development (views, templates, frontend)
- [x] Phase 6 — REST API
- [x] Phase 7 — Production deployment (Render, Cloudinary, WhiteNoise, security hardening)

---

## Licence

MIT