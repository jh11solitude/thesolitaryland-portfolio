from io import BytesIO
from PIL import Image
from django.contrib import admin
from django import forms
from django.core.files.base import ContentFile
from .models import Category, Tag, Photo, Video, Album, AlbumPhoto, FeaturedWork

# Register your models here.

# --- Helper Function for Universal Image Compression ---

def compress_uploaded_image(image_file):
    if image_file:
        img = Image.open(image_file)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        max_width, max_height = 2500, 2500
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        original_name = image_file.name.split('.')[0]
        new_filename = f"{original_name}.jpg"
        
        return ContentFile(buffer.read(), name=new_filename)
    return image_file


# Define the Custom Form to intercept the image asset

class PhotoAdminForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = '__all__'

    def clean_image(self):
        return compress_uploaded_image(self.cleaned_data.get('image'))


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = '__all__'

    def clean_thumbnail(self):
        return compress_uploaded_image(self.cleaned_data.get('thumbnail'))


class AlbumAdminForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = '__all__'

    def clean_cover_image(self):
        # This protects your Album page from crashing on large cover uploads!
        return compress_uploaded_image(self.cleaned_data.get('cover_image'))


# --- Model Admin Registrations --

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
    # Hook up the custom form to the existing PhotoAdmin class
    form = PhotoAdminForm  # <--- Crucial link injecting our compression filter
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
    form = VideoAdminForm
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
    form = AlbumAdminForm  # Hooked up to compress the Album cover image safely
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