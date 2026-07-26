"""
API Tests for the TheSolitaryLand Portfolio.

Test philosophy:
  - Test behaviour, not implementation
  - Each test has ONE clear assertion of intent
  - Tests are independent — each creates its own data
  - We test the happy path AND the failure cases

WHY we use APITestCase and not TestCase:
  DRF's APITestCase gives us self.client as a DRF APIClient,
  which handles JSON serialisation and Content-Type headers
  automatically. TestCase's client is Django's HTML client.

Running tests:
  python manage.py test apps.api
  python manage.py test apps.api.tests.PhotoAPITests
  python manage.py test apps.api.tests.PhotoAPITests.test_photo_list_returns_published_only
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.portfolio.models import Category, Tag, Photo, Video, Album, AlbumPhoto
from apps.contact.models import ContactMessage
import tempfile
from PIL import Image
import os


# ─────────────────────────────────────────────────────────────────
# TEST HELPERS
# ─────────────────────────────────────────────────────────────────

def create_temp_image():
    """
    Creates a real (tiny) JPEG image in a temp file.
    WHY: ImageField validation requires an actual image file,
    not just a filename string.
    """
    img = Image.new('RGB', (10, 10), color=(100, 100, 100))
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(tmp.name, format='JPEG')
    return tmp.name


def make_category(name='Travel'):
    return Category.objects.create(name=name, slug=name.lower())


def make_photo(title='Test Photo', category=None, published=True, featured=False):
    """Helper to create a Photo with a real image file."""
    tmp_path = create_temp_image()
    photo = Photo.objects.create(
        title=title,
        slug=title.lower().replace(' ', '-'),
        is_published=published,
        is_featured=featured,
        category=category,
        location='Singapore',
    )
    # Assign the image field to the temp file path
    photo.image.name = os.path.basename(tmp_path)
    photo.save()
    return photo


# ─────────────────────────────────────────────────────────────────
# PHOTO TESTS
# ─────────────────────────────────────────────────────────────────

class PhotoAPITests(APITestCase):

    def setUp(self):
        """
        setUp() runs before EVERY test method.
        Each test gets a clean, isolated state.
        """
        self.category_travel = make_category('Travel')
        self.category_street = make_category('Street')

        self.photo_published = make_photo(
            title='Published Photo',
            category=self.category_travel,
            published=True
        )
        self.photo_draft = make_photo(
            title='Draft Photo',
            category=self.category_travel,
            published=False
        )
        self.photo_featured = make_photo(
            title='Featured Photo',
            category=self.category_street,
            published=True,
            featured=True
        )

    # ── List endpoint ──────────────────────────────────────────

    def test_photo_list_returns_200(self):
        """The list endpoint should be accessible."""
        url = reverse('api:photo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_photo_list_returns_published_only(self):
        """
        Draft photos must never appear in the public API.
        This is the most important security behaviour to test.
        """
        url = reverse('api:photo-list')
        response = self.client.get(url)
        titles = [p['title'] for p in response.data['results']]
        self.assertIn('Published Photo', titles)
        self.assertNotIn('Draft Photo', titles)

    def test_photo_list_response_shape(self):
        """List serializer includes exactly the fields we expect."""
        url = reverse('api:photo-list')
        response = self.client.get(url)
        photo = response.data['results'][0]

        expected_fields = {'id', 'title', 'slug', 'image_url', 'location',
                           'category', 'view_count', 'created_at'}
        self.assertEqual(set(photo.keys()), expected_fields)

        # Detail fields should NOT be in list response (lean serializer)
        self.assertNotIn('description', photo)
        self.assertNotIn('camera_info', photo)
        self.assertNotIn('tags', photo)

    def test_photo_list_category_filter(self):
        """?category=street should return only street photos."""
        url = reverse('api:photo-list')
        response = self.client.get(url, {'category': 'street'})
        titles = [p['title'] for p in response.data['results']]
        self.assertIn('Featured Photo', titles)
        self.assertNotIn('Published Photo', titles)

    def test_photo_list_pagination_structure(self):
        """Response must include DRF pagination envelope."""
        url = reverse('api:photo-list')
        response = self.client.get(url)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    # ── Featured endpoint ──────────────────────────────────────

    def test_featured_endpoint_returns_featured_only(self):
        """Only is_featured=True photos should appear here."""
        url = reverse('api:photo-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in response.data['results']]
        self.assertIn('Featured Photo', titles)
        self.assertNotIn('Published Photo', titles)

    # ── Detail endpoint ────────────────────────────────────────

    def test_photo_detail_returns_200_for_published(self):
        """Published photo detail should be accessible by slug."""
        url = reverse('api:photo-detail', kwargs={'slug': 'published-photo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_photo_detail_returns_404_for_draft(self):
        """
        Draft photos must return 404 — not just be hidden from lists.
        A user who guesses the slug should not access draft content.
        """
        url = reverse('api:photo-detail', kwargs={'slug': 'draft-photo'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_photo_detail_includes_full_fields(self):
        """Detail serializer includes description, camera_info, tags."""
        url = reverse('api:photo-detail', kwargs={'slug': 'published-photo'})
        response = self.client.get(url)
        self.assertIn('description', response.data)
        self.assertIn('camera_info', response.data)
        self.assertIn('tags', response.data)

    def test_photo_detail_increments_view_count(self):
        """Each visit to the detail endpoint should increment view_count."""
        url = reverse('api:photo-detail', kwargs={'slug': 'published-photo'})
        initial_count = self.photo_published.view_count

        self.client.get(url)
        self.photo_published.refresh_from_db()
        self.assertEqual(self.photo_published.view_count, initial_count + 1)

        self.client.get(url)
        self.photo_published.refresh_from_db()
        self.assertEqual(self.photo_published.view_count, initial_count + 2)


# ─────────────────────────────────────────────────────────────────
# VIDEO TESTS
# ─────────────────────────────────────────────────────────────────

class VideoAPITests(APITestCase):

    def setUp(self):
        self.category = make_category('Documentary')
        self.video = Video.objects.create(
            title='Test Video',
            slug='test-video',
            video_type=Video.VideoType.YOUTUBE,
            embed_url='https://www.youtube.com/watch?v=test123',
            is_published=True,
            category=self.category,
        )
        self.draft_video = Video.objects.create(
            title='Draft Video',
            slug='draft-video',
            video_type=Video.VideoType.YOUTUBE,
            embed_url='https://www.youtube.com/watch?v=draft',
            is_published=False,
        )

    def test_video_list_returns_200(self):
        url = reverse('api:video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_video_list_excludes_drafts(self):
        url = reverse('api:video-list')
        response = self.client.get(url)
        titles = [v['title'] for v in response.data['results']]
        self.assertIn('Test Video', titles)
        self.assertNotIn('Draft Video', titles)

    def test_video_detail_returns_video_type_display(self):
        """
        video_type_display should return the human-readable label.
        'youtube' → 'YouTube Embed'
        """
        url = reverse('api:video-detail', kwargs={'slug': 'test-video'})
        response = self.client.get(url)
        self.assertEqual(response.data['video_type_display'], 'YouTube Embed')

    def test_video_filter_by_type(self):
        url = reverse('api:video-list')
        response = self.client.get(url, {'video_type': 'youtube'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for video in response.data['results']:
            self.assertEqual(video['video_type'], 'youtube')


# ─────────────────────────────────────────────────────────────────
# CONTACT TESTS
# ─────────────────────────────────────────────────────────────────

class ContactAPITests(APITestCase):

    def test_contact_post_creates_db_record(self):
        """A valid POST must persist a ContactMessage to the database."""
        url = reverse('api:contact')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test enquiry',
            'message': 'This is a test message that is long enough to pass validation.',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Test User')
        self.assertEqual(msg.email, 'test@example.com')

    def test_contact_post_returns_success_structure(self):
        """Success response must include status and message keys."""
        url = reverse('api:contact')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message that is long enough to pass validation.',
        }
        response = self.client.post(url, data, format='json')
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['status'], 'received')

    def test_contact_post_rejects_invalid_email(self):
        """Invalid email should return 400 with error on email field."""
        url = reverse('api:contact')
        data = {
            'name': 'Test User',
            'email': 'not-an-email',
            'message': 'This is a test message that is long enough.',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_contact_post_rejects_short_message(self):
        """
        Custom validator: messages under 20 chars should be rejected.
        This tests our validate_message() method in the serializer.
        """
        url = reverse('api:contact')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Too short.',  # Under 20 chars
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_contact_post_rejects_missing_required_fields(self):
        """Missing name, email, or message should return 400."""
        url = reverse('api:contact')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('message', response.data)

    def test_contact_get_not_allowed(self):
        """
        GET on the contact endpoint must return 405 Method Not Allowed.
        This tests that we haven't accidentally exposed contact data.
        """
        url = reverse('api:contact')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


# ─────────────────────────────────────────────────────────────────
# TAXONOMY TESTS
# ─────────────────────────────────────────────────────────────────

class TaxonomyAPITests(APITestCase):

    def setUp(self):
        Category.objects.create(name='Travel', slug='travel')
        Category.objects.create(name='Street', slug='street')
        Tag.objects.create(name='golden hour', slug='golden-hour')

    def test_category_list_returns_all(self):
        """Categories endpoint has no pagination — returns full list."""
        url = reverse('api:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No 'results' key — pagination is disabled for categories
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    def test_tag_list_returns_all(self):
        url = reverse('api:tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_category_fields(self):
        """Category objects must include id, name, slug."""
        url = reverse('api:category-list')
        response = self.client.get(url)
        cat = response.data[0]
        self.assertIn('id', cat)
        self.assertIn('name', cat)
        self.assertIn('slug', cat)


# ─────────────────────────────────────────────────────────────────
# API ROOT TEST
# ─────────────────────────────────────────────────────────────────

class APIRootTests(APITestCase):

    def test_root_returns_endpoint_map(self):
        """API root should return version, author, and endpoints map."""
        url = reverse('api:root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('version', response.data)
        self.assertIn('endpoints', response.data)
        self.assertIn('photos', response.data['endpoints'])
        self.assertIn('contact', response.data['endpoints'])


