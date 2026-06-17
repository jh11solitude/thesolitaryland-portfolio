from django.db import models
from django.utils.text import slugify

# Category Model
class Category(models.Model):
    """
    Represents a photography/video genre.
    Examples: Travel, Street, Architecture, Nature, Urban
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"   # Fixes "Categorys" in Admin
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Tag Model
class Tag(models.Model):
    """
    Fine-grained labels for photos and videos.
    Examples: golden-hour, singapore, 35mm, long-exposure
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Photo Model
class Photo(models.Model):
    """
    A single photograph. The core content unit of the portfolio.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(
        blank=True,
        help_text="The story behind this shot. Shown on the detail page."
    )

    # The actual image file
    image = models.ImageField(upload_to='photos/%Y/%m/')
    # upload_to='photos/%Y/%m/' means files are organized:
    # media/photos/2025/01/my-photo.jpg

    # Metadata
    location = models.CharField(max_length=200, blank=True)
    camera_info = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. Sony A7IV + 35mm f/1.4 @ f/2.0, 1/500s, ISO 400"
    )
    taken_at = models.DateField(
        null=True,
        blank=True,
        help_text="Date the photo was taken"
    )

    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photos'
        # related_name lets you do: category.photos.all()
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='photos'
    )

    # Editorial control
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(
        default=False,
        help_text="Show this photo in featured sections"
    )

    # Analytics
    view_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']   # Newest first by default

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Video Model
class Video(models.Model):
    """
    A video work — either a self-hosted MP4 or a YouTube/Vimeo embed.
    """

    class VideoType(models.TextChoices):
        # (database_value, human_readable_label)
        UPLOAD = 'upload', 'Self-hosted (MP4)'
        YOUTUBE = 'youtube', 'YouTube Embed'
        VIMEO = 'vimeo', 'Vimeo Embed'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)

    # Source — only one of these will be used, depending on video_type
    video_type = models.CharField(
        max_length=20,
        choices=VideoType.choices,
        default=VideoType.YOUTUBE
    )
    video_file = models.FileField(
        upload_to='videos/%Y/%m/',
        null=True,
        blank=True,
        help_text="Only for self-hosted MP4 uploads"
    )
    embed_url = models.URLField(
        blank=True,
        help_text="Full YouTube or Vimeo URL e.g. https://www.youtube.com/watch?v=..."
    )

    # Thumbnail shown in the video grid
    thumbnail = models.ImageField(
        upload_to='video_thumbnails/%Y/%m/',
        null=True,
        blank=True
    )

    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='videos'
    )

    # Editorial
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_video_type_display()})"
        # get_video_type_display() returns the human label, e.g. "YouTube Embed"


# Album Model
class Album(models.Model):
    """
    A curated series of photos — e.g. 'Japan 2024', 'Architecture Vol.1'
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(
        upload_to='album_covers/',
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # ManyToMany WITH a through-table so we can order photos
    photos = models.ManyToManyField(
        Photo,
        through='AlbumPhoto',
        related_name='albums'
    )

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# AlbumPhoto Model
class AlbumPhoto(models.Model):
    """
    Through-table connecting Album to Photo.
    Stores the display order of each photo within its album.
    """
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('album', 'photo')
        # Prevents the same photo appearing twice in one album

    def __str__(self):
        return f"{self.album.title} — {self.photo.title} (#{self.order})"

# FeaturedWork Model
class FeaturedWork(models.Model):
    """
    Controls what appears on the homepage.
    Each row is one featured item — either a Photo or a Video.
    Managed entirely via Django Admin.
    """
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Override display title (optional — defaults to photo/video title)"
    )

    # Point to either a photo or a video (one must be set)
    photo = models.ForeignKey(
        Photo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_as'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_as'
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Featured Work"
        verbose_name_plural = "Featured Works"

    def clean(self):
        """
        Model-level validation: exactly one of photo or video must be set.
        Django calls this automatically before saving via Admin.
        """
        from django.core.exceptions import ValidationError
        if not self.photo and not self.video:
            raise ValidationError(
                "A featured work must link to either a Photo or a Video."
            )
        if self.photo and self.video:
            raise ValidationError(
                "A featured work can only link to one item — Photo OR Video, not both."
            )

    def get_item(self):
        """Convenience method — returns whichever item is set."""
        return self.photo or self.video

    def __str__(self):
        item = self.get_item()
        return f"Featured: {item.title} (order {self.display_order})"