from django.views.generic import ListView, DetailView
from .models import Photo, Video, Album, Category, Tag
from django.db.models import F


# Create your views here.
class PhotoListView(ListView):
    """
    The main photography gallery page.
    Supports optional ?category=<slug> filtering.
    Paginates at 50 photos per page.
    """
    model = Photo
    template_name = 'portfolio/photo_list.html'
    context_object_name = 'photos'
    paginate_by = 50

    def get_queryset(self):
        """
        Returns published photos only.
        Filters by category slug if ?category= is in the URL.
 
        WHY select_related:
          Without it, accessing photo.category in the template
          fires a separate SQL query per photo (N+1 problem).
          select_related('category') fetches everything in one JOIN query.
        """
        qs = (
            Photo.objects
            .filter(is_published=True)
            .select_related('category')
            .prefetch_related('tags')
            .order_by('-created_at')
        )
 
        # Apply category filter if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
 
        return qs
 
    def get_context_data(self, **kwargs):
        """
        Inject additional data into the template context:
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['active_category'] = self.request.GET.get('category', 'all')
        return context


class PhotoDetailView(DetailView):
    """
    Single photo page. Increments view count on each visit.
    Uses slug for SEO-friendly URLs instead of pk.
    """
    model = Photo
    template_name = 'portfolio/photo_detail.html'
    context_object_name = 'photo'

    def get_queryset(self):
        """Only show published photos."""
        return Photo.objects.filter(is_published=True).select_related('category').prefetch_related('tags')
 
    def get_object(self, queryset=None):
        """
        Increment view count atomically using F() expression.
 
        WHY F() and not photo.view_count += 1:
          If two users hit this page simultaneously, both would read
          view_count=5, both would set it to 6 — losing one count.
          F('view_count') + 1 lets PostgreSQL do the increment inside
          the database where it's atomic and race-condition-safe.
        """
        obj = super().get_object(queryset)
        Photo.objects.filter(pk=obj.pk).update(view_count=F('view_count') + 1)
        return obj
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related photos: same category, excluding current, latest 8
        photo = self.object
        if photo.category:
            context['related_photos'] = (
                Photo.objects
                .filter(is_published=True, category=photo.category)
                .exclude(pk=photo.pk)
                .order_by('-created_at')[:8]
            )
        else:
            context['related_photos'] = Photo.objects.none()
 
        return context


# ─────────────────────────────────────────────────────────────────
# VIDEO
# ─────────────────────────────────────────────────────────────────

class VideoListView(ListView):
    """
    The video portfolio grid.
    Supports the same ?category= filter as photos.
    """
    model = Video
    template_name = 'portfolio/video_list.html'
    context_object_name = 'videos'
    paginate_by = 24
 
    def get_queryset(self):
        qs = (
            Video.objects
            .filter(is_published=True)
            .select_related('category')
            .order_by('-created_at')
        )
 
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
 
        return qs
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['active_category'] = self.request.GET.get('category', 'all')
        return context


# ─────────────────────────────────────────────────────────────────
# ALBUMS
# ─────────────────────────────────────────────────────────────────

class AlbumListView(ListView):
    """Album series index page."""
    model = Album
    template_name = 'portfolio/album_list.html'
    context_object_name = 'albums'
 
    def get_queryset(self):
        return (
            Album.objects
            .filter(is_published=True)
            .prefetch_related('photos')
            .order_by('-created_at')
        )


class AlbumDetailView(DetailView):
    """
    Single album page showing its photos in order.
    AlbumPhoto through-table ordering is respected via prefetch.
    """
    model = Album
    template_name = 'portfolio/album_detail.html'
    context_object_name = 'album'
 
    def get_queryset(self):
        return Album.objects.filter(is_published=True)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object
 
        # Fetch photos in album-defined order (AlbumPhoto.order field)
        context['album_photos'] = (
            album.photos
            .filter(is_published=True)
            .order_by('albumphoto__order')
        )
        return context