"""
API views for the TheSolitaryLand Portfolio.

All read endpoints (photos, videos, albums, categories, tags) are
GET-only. The only write endpoint is the contact form (POST).

View class choices:
  ListAPIView     → GET /resource/         (list of objects)
  RetrieveAPIView → GET /resource/<slug>/  (single object)
  CreateAPIView   → POST /resource/        (create, contact only)

We use slug lookups instead of pk for SEO-friendly URLs.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.portfolio.models import Photo, Video, Album, Category, Tag
from apps.contact.models import ContactMessage
from .serializers import (
    PhotoListSerializer, PhotoDetailSerializer,
    VideoListSerializer, VideoDetailSerializer,
    AlbumListSerializer, AlbumDetailSerializer,
    CategorySerializer, TagSerializer,
    ContactSerializer,
)
from .filters import PhotoFilter, VideoFilter


# ─────────────────────────────────────────────────────────────────
# PHOTO ENDPOINTS
# ─────────────────────────────────────────────────────────────────

@extend_schema(
    summary="List all published photos",
    description="Returns a paginated list of published photographs. Supports filtering by category, tag, location, and date range.",
    parameters=[
        OpenApiParameter('category', str, description='Filter by category slug e.g. travel'),
        OpenApiParameter('tag', str, description='Filter by tag slug e.g. golden-hour'),
        OpenApiParameter('is_featured', bool, description='Return featured photos only'),
        OpenApiParameter('search', str, description='Search title, description, location'),
        OpenApiParameter('ordering', str, description='Order by field e.g. -created_at, view_count'),
    ]
)
class PhotoListView(generics.ListAPIView):
    """
    GET /api/v1/photos/

    WHY select_related + prefetch_related here:
    - select_related('category')  → one SQL JOIN for category (ForeignKey)
    - prefetch_related('tags')    → one additional query for all tags
                                    (ManyToMany — can't use JOIN efficiently)

    Without these, accessing photo.category in the serializer
    would fire a new query for EVERY photo in the list.
    50 photos × 2 queries each = 101 queries instead of 2.
    This is the N+1 query problem — a classic performance bug.
    """
    serializer_class = PhotoListSerializer
    filterset_class = PhotoFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'view_count', 'title', 'taken_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Photo.objects
            .filter(is_published=True)
            .select_related('category')
            .prefetch_related('tags')
        )


@extend_schema(
    summary="Get a single photo by slug",
    description="Returns full photo detail including description, camera info, tags, and view count. Each call increments the view counter."
)
class PhotoDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/photos/<slug>/

    Uses slug as the lookup field instead of pk.
    lookup_field tells DRF which model field to match against the URL parameter.
    """
    serializer_class = PhotoDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Photo.objects
            .filter(is_published=True)
            .select_related('category')
            .prefetch_related('tags')
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve() to increment view count before returning.
        We use get_object() which handles 404 automatically if not found.
        """
        instance = self.get_object()

        Photo.objects.filter(pk=instance.pk).update(
            view_count=F('view_count') + 1
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema(
    summary="List featured photos",
    description="Returns photos marked as featured, ordered by newest first."
)
class PhotoFeaturedView(generics.ListAPIView):
    """
    GET /api/v1/photos/featured/

    WHY a dedicated endpoint instead of ?is_featured=true:
    A named endpoint is more intentional — it's part of the API
    contract. Filtering is for dynamic exploration; a dedicated
    endpoint communicates a specific editorial concept.
    """
    serializer_class = PhotoListSerializer

    def get_queryset(self):
        return (
            Photo.objects
            .filter(is_published=True, is_featured=True)
            .select_related('category')
            .order_by('-created_at')
        )


# ─────────────────────────────────────────────────────────────────
# VIDEO ENDPOINTS
# ─────────────────────────────────────────────────────────────────

class VideoListView(generics.ListAPIView):
    """GET /api/v1/videos/"""
    serializer_class = VideoListSerializer
    filterset_class = VideoFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Video.objects
            .filter(is_published=True)
            .select_related('category')
        )


class VideoDetailView(generics.RetrieveAPIView):
    """GET /api/v1/videos/<slug>/"""
    serializer_class = VideoDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Video.objects
            .filter(is_published=True)
            .select_related('category')
            .prefetch_related('tags')
        )


# ─────────────────────────────────────────────────────────────────
# ALBUM ENDPOINTS
# ─────────────────────────────────────────────────────────────────

class AlbumListView(generics.ListAPIView):
    """GET /api/v1/albums/"""
    serializer_class = AlbumListSerializer
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Album.objects
            .filter(is_published=True)
            .prefetch_related('photos')
        )


class AlbumDetailView(generics.RetrieveAPIView):
    """GET /api/v1/albums/<slug>/"""
    serializer_class = AlbumDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Album.objects
            .filter(is_published=True)
            .prefetch_related('photos')
        )


# ─────────────────────────────────────────────────────────────────
# CATEGORY + TAG ENDPOINTS
# ─────────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    """
    GET /api/v1/categories/

    No pagination on categories — there won't be more than ~20.
    We override pagination_class to None to return the full list.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('name')
    pagination_class = None


class TagListView(generics.ListAPIView):
    """GET /api/v1/tags/"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by('name')
    pagination_class = None


# ─────────────────────────────────────────────────────────────────
# CONTACT ENDPOINT
# ─────────────────────────────────────────────────────────────────

@extend_schema(
    summary="Submit a contact message",
    description="POST a contact message. Saved to the database and triggers an email notification to the site owner.",
    responses={
        201: {"description": "Message received"},
        400: {"description": "Validation error"},
    }
)
class ContactCreateView(generics.CreateAPIView):
    """
    POST /api/v1/contact/

    WHY CreateAPIView and not a plain APIView:
    CreateAPIView handles the request → serializer → validate →
    save flow automatically. We only override create() to
    customise the success response.

    The serializer handles validation.
    The model's save() persists to the database.
    We add email notification on top.
    """
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # raise_exception=True means DRF automatically returns a
        # 400 response with validation errors if is_valid() fails

        # Save to database
        contact_msg = serializer.save()

        # Send email (non-fatal failure)
        from django.core.mail import send_mail
        from django.conf import settings
        try:
            send_mail(
                subject=f"Portfolio enquiry from {contact_msg.name}",
                message=f"From: {contact_msg.name} <{contact_msg.email}>\n\n{contact_msg.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        # Return a clean success response — not the model data
        # (all fields are write_only in the serializer anyway)
        return Response(
            {
                'status': 'received',
                'message': "Thank you. I'll be in touch soon."
            },
            status=status.HTTP_201_CREATED
        )


# ─────────────────────────────────────────────────────────────────
# API ROOT — a friendly index of all endpoints
# ─────────────────────────────────────────────────────────────────

class APIRootView(APIView):
    """
    GET /api/v1/

    Returns a map of all available endpoints.
    This is good API design — a consumer can discover the API
    structure from the root without reading documentation.
    """

    def get(self, request):
        base = request.build_absolute_uri('/api/v1')
        return Response({
            'version': '1.0.0',
            'author': 'TheSolitaryLand',
            'endpoints': {
                'photos': f'{base}/photos/',
                'photo': f'{base}/photos/<slug>/',
                'featured': f'{base}/photos/featured/',
                'videos': f'{base}/videos/',
                'video': f'{base}/videos/<slug>/',
                'albums': f'{base}/albums/',
                'album': f'{base}/albums/<slug>/',
                'categories': f'{base}/categories/',
                'tags': f'{base}/tags/',
                'contact': f'{base}/contact/',
                'docs': f'{base}/docs/',
                'schema': f'{base}/schema/',
            }
        })


