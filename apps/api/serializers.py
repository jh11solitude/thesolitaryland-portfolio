from rest_framework import serializers
from apps.portfolio.models import (
    Category, Tag, Photo, Video, Album, AlbumPhoto
)
from apps.contact.models import ContactMessage


# ─────────────────────────────────────────────────────────────────
# UTILITY / NESTED SERIALIZERS
# These are small serializers used *inside* larger ones (nesting).
# ─────────────────────────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    """
    Minimal category representation.
    Used nested inside Photo and Video serializers.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    """Minimal tag representation."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


# ─────────────────────────────────────────────────────────────────
# PHOTO SERIALIZERS
# ─────────────────────────────────────────────────────────────────

class PhotoListSerializer(serializers.ModelSerializer):
    """
    Lean serializer for the photo list endpoint.

    WHY lean: this response may contain 50 photos. We only include
    fields the gallery grid actually needs — image URL, title, slug,
    category, and location. Full description/camera info is omitted.

    image_url vs image:
    - photo.image is a Django FieldFile (Python object)
    - We need the full URL string for the API consumer
    - SerializerMethodField lets us call .url on it safely
    - We check if the file exists before calling .url to prevent
      crashes if an image was accidentally deleted from disk
    """
    category = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            'id',
            'title',
            'slug',
            'image_url',
            'location',
            'category',
            'view_count',
            'created_at',
        ]

    def get_image_url(self, obj):
        """Return the absolute URL to the image file."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    



class PhotoDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for the photo detail endpoint.
    Includes all fields — description, camera info, tags, timestamps.

    category and tags are nested (show full objects, not just IDs).
    This is called "depth" in DRF — we control it explicitly rather
    than using the automatic depth=1 which gives you less control.
    """
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    related_photos = serializers.SerializerMethodField() 

    class Meta:
        model = Photo
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'image_url',
            'location',
            'camera_info',
            'taken_at',
            'category',
            'tags',
            'view_count',
            'is_featured',
            'created_at',
            'updated_at',
            'related_photos',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_related_photos(self, obj):
        """
        Fetches the latest 8 photos within the same category, excluding the current photo.
        Replicates the exact business logic from your MVT PhotoDetailView.
        """
        if not obj.category:
            return []

        # 1. Fetch the related database records
        queryset = (
            Photo.objects
            .filter(is_published=True, category=obj.category)
            .exclude(pk=obj.pk)
            .order_by('-created_at')[:8]
        )

        # 2. Re-serialize them dynamically using a minimal inline schema 
        # to prevent nested loops or heavy database recursion.
        return MiniPhotoSerializer(queryset, many=True, context=self.context).data


class MiniPhotoSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer used exclusively to output the 
    minimal data structure needed for the related photos tray.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            'id', 
            'title', 
            'slug', 
            'image_url', 
            'created_at'
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ─────────────────────────────────────────────────────────────────
# VIDEO SERIALIZERS
# ─────────────────────────────────────────────────────────────────

class VideoListSerializer(serializers.ModelSerializer):
    """
    Lean serializer for the video grid.
    video_type_display converts 'youtube' → 'YouTube Embed' etc.
    """
    category = CategorySerializer(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    video_type_display = serializers.CharField(
        source='get_video_type_display',
        read_only=True
    )

    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'slug',
            'video_type',
            'video_type_display',
            'thumbnail_url',
            'category',
            'created_at',
        ]

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class VideoDetailSerializer(serializers.ModelSerializer):
    """
    Full video serializer.

    WHY we include both video_file_url and embed_url:
    The API consumer needs to handle either case. We expose both
    fields and let the consumer check video_type to know which
    one to use. Only one will be non-null for any given video.
    """
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    video_file_url = serializers.SerializerMethodField()
    video_type_display = serializers.CharField(
        source='get_video_type_display',
        read_only=True
    )

    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'video_type',
            'video_type_display',
            'video_file_url',
            'embed_url',
            'thumbnail_url',
            'category',
            'tags',
            'is_featured',
            'created_at',
            'updated_at',
        ]

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_video_file_url(self, obj):
        request = self.context.get('request')
        if obj.video_file and request:
            return request.build_absolute_uri(obj.video_file.url)
        return None


# ─────────────────────────────────────────────────────────────────
# ALBUM SERIALIZERS
# ─────────────────────────────────────────────────────────────────

class AlbumListSerializer(serializers.ModelSerializer):
    """
    Album card for the series index.
    photo_count is a computed field — not stored in the database,
    derived at query time.
    """
    cover_image_url = serializers.SerializerMethodField()
    photo_count = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'cover_image_url',
            'photo_count',
            'created_at',
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_photo_count(self, obj):
        """
        WHY we use a method instead of annotating in the view:
        This keeps the serializer self-contained. The trade-off is
        an extra query per album for the count. In advanced development,
        we'll move this to an annotation for better performance.
        """
        return obj.photos.filter(is_published=True).count()


class AlbumDetailSerializer(serializers.ModelSerializer):
    """
    Full album with its photos in their defined order.

    The photos are fetched through the AlbumPhoto through-table
    and ordered by the 'order' field we defined in Phase 2.
    We use PhotoListSerializer for each photo — lean but sufficient
    for the album grid view.
    """
    cover_image_url = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'cover_image_url',
            'photos',
            'created_at',
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_photos(self, obj):
        """
        Fetch photos in album-defined order via the through-table.
        Only published photos are included.
        """
        ordered_photos = (
            obj.photos
            .filter(is_published=True)
            .order_by('albumphoto__order')
        )
        return PhotoListSerializer(
            ordered_photos,
            many=True,
            context=self.context    # Pass request context so image_url works
        ).data


# ─────────────────────────────────────────────────────────────────
# CONTACT SERIALIZER
# ─────────────────────────────────────────────────────────────────

class ContactSerializer(serializers.ModelSerializer):
    """
    Write-only serializer for contact form submission via API.

    WHY write_only on all fields:
    This serializer is used for POST requests only. We don't want
    the API to expose contact submissions back to the requester
    (and certainly not to other users). write_only=True means the
    field is accepted on input but never included in the response.

    On success, we return a simple confirmation message instead.
    """

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        extra_kwargs = {
            'name':    {'write_only': True},
            'email':   {'write_only': True},
            'subject': {'write_only': True, 'required': False},
            'message': {'write_only': True},
        }

    def validate_message(self, value):
        """
        Custom field-level validation.
        Reject messages that are suspiciously short (likely spam/test).

        Naming convention: validate_<field_name>(self, value)
        DRF calls this automatically during serializer.is_valid()
        """
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                "Please write a meaningful message (at least 20 characters)."
            )
        return value

    def validate(self, data):
        """
        Object-level validation — runs after all field-level validation.
        Use this for cross-field validation (e.g. two fields that depend
        on each other). Here we use it to strip whitespace from all fields.
        """
        data['name'] = data.get('name', '').strip()
        data['message'] = data.get('message', '').strip()
        return data