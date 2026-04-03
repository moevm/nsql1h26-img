from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Image

User = get_user_model()


class ImageAPITestCase(APITestCase):
    def setUp(self):
        # Setup test users
        self.author = User.objects.create_user(
            username="author", email="author@test.com", password="123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="123"
        )

        # Resolve endpoint URL
        self.list_url = reverse("image-list")

        # 1x1 GIF payload for file uploads
        self.pixel_gif = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
            b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        )

    def generate_dummy_file(self, filename="test.gif"):
        """Helper to generate mock image file"""
        return SimpleUploadedFile(filename, self.pixel_gif, content_type="image/gif")

    # READ & CREATE TESTS

    def test_get_images_list(self):
        # Ensure public access to list endpoint
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_image_unauthenticated(self):
        # Assert 401 Unauthorized for anonymous POST
        response = self.client.post(self.list_url, {"title": "Test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_image_success(self):
        # Assert 201 Created and DB write for authenticated POST
        self.client.force_authenticate(user=self.author)
        data = {
            "title": "My Awesome Pic",
            "description": "Landscape",
            "file": self.generate_dummy_file(),
        }
        response = self.client.post(self.list_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.first().author, self.author)

    # PERMISSION TESTS (UPDATE & DELETE)

    def test_update_image_permissions(self):
        image = Image.objects.create(
            title="Original", author=self.author, file=self.generate_dummy_file()
        )
        detail_url = reverse("image-detail", kwargs={"pk": image.id})

        # Assert 403 Forbidden for non-author patch
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(detail_url, {"title": "Hacked"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Assert 200 OK for author patch
        self.client.force_authenticate(user=self.author)
        response = self.client.patch(detail_url, {"title": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_image_permissions(self):
        image = Image.objects.create(
            title="To Delete", author=self.author, file=self.generate_dummy_file()
        )
        detail_url = reverse("image-detail", kwargs={"pk": image.id})

        # Assert 403 Forbidden for non-author delete
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Assert 204 No Content for author delete
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 0)

    # FILTERING & SEARCH TESTS

    def test_search_and_filters(self):
        Image.objects.create(
            title="Cute white cat",
            description="Animal",
            author=self.author,
            file=self.generate_dummy_file("cat.gif"),
        )
        Image.objects.create(
            title="Funny black dog",
            description="Animal",
            author=self.author,
            file=self.generate_dummy_file("dog.gif"),
        )

        # Assert exact match filter logic
        response_filter = self.client.get(self.list_url, {"image_format": "GIF"})
        self.assertEqual(response_filter.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_filter.data["results"]), 2)

        # Assert search substring logic over title
        response_search = self.client.get(self.list_url, {"search": "Cute"})
        self.assertEqual(response_search.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response_search.data["results"]), 1)
        self.assertEqual(response_search.data["results"][0]["title"], "Cute white cat")
