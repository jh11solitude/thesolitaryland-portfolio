from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Photo, Video, Album

# Create your views here.
class PhotoListView(ListView):
    model = Photo
    template_name = 'portfolio/photo_list.html'
    context_object_name = 'photos'

class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'portfolio/photo_detail.html'

class VideoListView(ListView):
    model = Video
    template_name = 'portfolio/video_list.html'

class AlbumListView(ListView):
    model = Album
    template_name = 'portfolio/album_list.html'

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'portfolio/album_detail.html'