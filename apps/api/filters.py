"""
FilterSet classes for the Portfolio API.

django-filter reads these classes and generates the WHERE clauses
in your SQL queries based on query parameters in the URL.

Examples of what these enable:
  /api/v1/photos/?category=travel
  /api/v1/photos/?tag=golden-hour&category=street
  /api/v1/photos/?is_featured=true
  /api/v1/videos/?video_type=youtube
"""

import django_filters
from apps.portfolio.models import Photo, Video, Category, Tag


class PhotoFilter(django_filters.FilterSet):
    """
    Filterset for the Photo list endpoint.

    Each field here becomes a valid query parameter.
    The filter type controls how it's applied:

    - CharFilter with lookup_expr='exact' → WHERE category__slug = 'travel'
    - BooleanFilter → WHERE is_featured = true
    - ModelMultipleChoiceFilter → WHERE id IN (tag1, tag2) — supports multiple values
    """

    # Filter by category slug: ?category=travel
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact',
        label='Category slug'
    )

    # Filter by tag slug: ?tag=golden-hour
    # ModelMultipleChoiceFilter allows ?tag=golden-hour&tag=singapore
    tag = django_filters.ModelMultipleChoiceFilter(
        field_name='tags',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Tag slug(s)'
    )

    # Filter featured only: ?is_featured=true
    is_featured = django_filters.BooleanFilter(
        field_name='is_featured',
        label='Featured only'
    )

    # Filter by location (partial match): ?location=singapore
    location = django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains',
        # icontains = case-insensitive contains
        # WHERE location ILIKE '%singapore%'
        label='Location (partial)'
    )

    # Date range filters: ?taken_after=2024-01-01&taken_before=2024-12-31
    taken_after = django_filters.DateFilter(
        field_name='taken_at',
        lookup_expr='gte',
        label='Taken on or after'
    )
    taken_before = django_filters.DateFilter(
        field_name='taken_at',
        lookup_expr='lte',
        label='Taken on or before'
    )

    class Meta:
        model = Photo
        fields = ['category', 'tag', 'is_featured', 'location', 'taken_after', 'taken_before']


class VideoFilter(django_filters.FilterSet):
    """
    Filterset for the Video list endpoint.
    """

    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact',
        label='Category slug'
    )

    # Filter by video type: ?video_type=youtube
    video_type = django_filters.ChoiceFilter(
        choices=[
            ('upload', 'Self-hosted'),
            ('youtube', 'YouTube'),
            ('vimeo', 'Vimeo'),
        ],
        label='Video type'
    )

    is_featured = django_filters.BooleanFilter(
        field_name='is_featured'
    )

    class Meta:
        model = Video
        fields = ['category', 'video_type', 'is_featured']