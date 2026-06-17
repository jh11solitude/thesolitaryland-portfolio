from django.urls import path
from . import views

app_name = 'portfolio'   # Namespace prevents URL name collisions between apps

urlpatterns = [
    # These views don't exist yet — we build them in Phase 5
    path('photos/', views.PhotoListView.as_view(), name='photo-list'),
    path('photos/<slug:slug>/', views.PhotoDetailView.as_view(), name='photo-detail'),
    path('videos/', views.VideoListView.as_view(), name='video-list'),
    path('albums/', views.AlbumListView.as_view(), name='album-list'),
    path('albums/<slug:slug>/', views.AlbumDetailView.as_view(), name='album-detail'),
]