from django.contrib import admin
from .models import Category, Tag, Photo, Video, Album, AlbumPhoto, FeaturedWork

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    # prepopulated_fields auto-fills slug as you type the name — very useful


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'is_featured', 'view_count', 'created_at']
    list_filter = ['is_published', 'is_featured', 'category']
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    # list_editable lets you toggle publish/feature directly from the list view
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    # filter_horizontal gives a nice two-panel widget for ManyToMany fields


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_type', 'category', 'is_published', 'is_featured', 'created_at']
    list_filter = ['is_published', 'is_featured', 'video_type', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    filter_horizontal = ['tags']


class AlbumPhotoInline(admin.TabularInline):
    # Inline lets you manage AlbumPhotos directly inside the Album admin page
    model = AlbumPhoto
    extra = 3             # Show 3 empty rows for adding photos
    ordering = ['order']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    inlines = [AlbumPhotoInline]
    # This embeds the AlbumPhoto through-table directly on the Album page


@admin.register(FeaturedWork)
class FeaturedWorkAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    ordering = ['display_order']