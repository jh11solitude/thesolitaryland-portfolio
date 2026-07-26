"""
API URL configuration — /api/v1/

URL pattern decisions:
- We use <slug:slug> not <int:pk> everywhere for SEO-friendly URLs
- The 'featured' endpoint is registered BEFORE <slug:slug> to prevent
  Django from treating 'featured' as a slug value
- app_name = 'api' creates a URL namespace (reverse as 'api:photo-list')
"""

from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from . import views

app_name = 'api'

urlpatterns = [

    # ── API Root ──────────────────────────────────────────────
    path('', views.APIRootView.as_view(), name='root'),

    # ── Photos ────────────────────────────────────────────────
    # ORDER MATTERS: 'featured/' must come before '<slug:slug>/'
    # Otherwise Django would match 'featured' as a photo slug
    path('photos/', views.PhotoListView.as_view(), name='photo-list'),
    path('photos/featured/', views.PhotoFeaturedView.as_view(), name='photo-featured'),
    path('photos/<slug:slug>/', views.PhotoDetailView.as_view(), name='photo-detail'),

    # ── Videos ───────────────────────────────────────────────
    path('videos/', views.VideoListView.as_view(), name='video-list'),
    path('videos/<slug:slug>/', views.VideoDetailView.as_view(), name='video-detail'),

    # ── Albums ────────────────────────────────────────────────
    path('albums/', views.AlbumListView.as_view(), name='album-list'),
    path('albums/<slug:slug>/', views.AlbumDetailView.as_view(), name='album-detail'),

    # ── Taxonomy ─────────────────────────────────────────────
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),

    # ── Contact ───────────────────────────────────────────────
    path('contact/', views.ContactCreateView.as_view(), name='contact'),

    # ── Auto-generated API documentation ─────────────────────
    # drf-spectacular reads your serializers and views and generates:
    # /api/v1/schema/ → raw OpenAPI YAML schema
    # /api/v1/docs/ → Swagger UI (interactive)
    # /api/v1/redoc/ → ReDoc UI (readable)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]