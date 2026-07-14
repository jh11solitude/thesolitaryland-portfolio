from django.views.generic import TemplateView
from apps.portfolio.models import FeaturedWork, Photo, Video


# Create your views here.
class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        """
        Inject homepage content:
        - featured_works: ordered FeaturedWork items (active only)
        - latest_photos: 24 newest published photos (fallback grid)
        """
        context = super().get_context_data(**kwargs)
 
        context['featured_works'] = (
            FeaturedWork.objects
            .filter(is_active=True)
            .select_related('photo', 'video')
            .order_by('display_order')
        )
 
        context['latest_photos'] = (
            Photo.objects
            .filter(is_published=True)
            .select_related('category')
            .order_by('-created_at')[:24]
        )
 
        return context

class AboutView(TemplateView):
    template_name = 'pages/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['disciplines'] = [
            "Portrait",
            "Landscape",
            "Street",
            "Cityscape",
            "Cinematic"
        ]
        return context