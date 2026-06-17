# TheSolitaryLand — Photography Portfolio

A cinematic personal brand website and Django-powered CMS for managing
photography, video, and visual storytelling work.

**Live site:** [thesolitaryland.com](https://thesolitaryland.com) *(coming soon)*  
**Tech stack:** Python · Django · PostgreSQL · Bootstrap · JavaScript

---

## Project Vision

Personal brand platform for TheSolitaryLand — Photographer · Visual Storyteller · Builder of Visual Systems.

Built to showcase photography and video work through a cinematic,
minimal frontend while demonstrating production-grade Django backend engineering.

---

## Features

**User-facing**
- Cinematic fullscreen hero with video background
- Photography gallery with category filtering and masonry layout
- Photo detail pages with story, location metadata, and camera info
- Video portfolio supporting MP4 uploads and YouTube/Vimeo embeds
- Album series pages (curated photo collections)
- About page and contact form

**Backend CMS (Django Admin)**
- Upload and manage photos, videos, and albums
- Category and tag assignment
- Featured content control for homepage
- Contact message inbox with read/unread status
- Publication draft workflow (publish when ready)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | Django 6.0.6 |
| Database | PostgreSQL |
| Frontend | HTML · CSS (Bootstrap 5) · JavaScript |
| Media | Pillow (ImageField) |
| Deployment | Render / Railway *(planned)* |

---

## Local Development Setup

**Prerequisites:** Python 3.14+, PostgreSQL

```bash
# 1. Clone the repo
git clone https://github.com/jh11solitude/thesolitaryland-portfolio.git
cd thesolitaryland-portfolio

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements/local.txt

# 4. Create PostgreSQL database
createdb thesolitaryland_portfolio

# 5. Configure environment variables
cp .env.example .env
# Edit .env with your database credentials and secret key

# 6. Run migrations
python manage.py migrate

# 7. Create admin user
python manage.py createsuperuser

# 8. Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` for the site, `http://127.0.0.1:8000/admin` for the CMS.

---

## Project Structure
thesolitaryland-portfolio/

├── apps/

│   ├── portfolio/      # Photos, Videos, Albums, Categories, Tags

│   ├── pages/          # Home and About views

│   └── contact/        # Contact form and message storage

├── config/

│   ├── settings/

│   │   ├── base.py     # Shared settings

│   │   ├── local.py    # Development

│   │   └── production.py

│   └── urls.py

├── templates/          # HTML templates

├── static/             # CSS, JS, images

├── requirements/

│   ├── base.txt

│   ├── local.txt

│   └── production.txt

└── manage.py

---

## Database Design

Eight models across two apps:

`Category` · `Tag` · `Photo` · `Video` · `Album` · `AlbumPhoto` · `FeaturedWork` · `ContactMessage`

See [Phase 2 design notes](#) for full ER diagram and model rationale.

---

## Skills Demonstrated

This project covers skills from the **Meta Back-End Developer Professional Certificate**:

- Django models, ORM, migrations
- Class-based views (ListView, DetailView, TemplateView)
- Django Admin customisation
- PostgreSQL integration
- REST API design with Django REST Framework *(in progress)*
- Git feature branch workflow
- Production deployment configuration

---

## Development Phases

- [x] Phase 1 — System blueprint and architecture design
- [x] Phase 2 — Database design and Django models
- [x] Phase 3 — Project setup, settings, Admin
- [x] Phase 4 — Git workflow and repository structure
- [ ] Phase 5 — Feature development (views, templates, frontend)
- [ ] Phase 6 — REST API
- [ ] Phase 7 — Production deployment

---

## Licence

MIT