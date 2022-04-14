from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from haleygg.tests.mixins import HaleyggUrlPatternsTestMixin


class MapTest(APITestCase, HaleyggUrlPatternsTestMixin):
    def setUp(self):
        self.map = {"name": "Sample Map"}
        self.url = reverse("map-list")

    def test_create_a_map(self):
        response = self.client.post(self.url, self.map)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        another_map = {"name": "Another map", "type": "melee"}
        response = self.client.post(self.url, another_map)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_a_map_using_invalid_type(self):
        self.map["type"] = "invalid_type"
        response = self.client.post(self.url, self.map)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_maps_using_conflicts_names(self):
        response = self.client.post(self.url, self.map)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, self.map)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_a_map_includes_image(self):
        self.map["image"] = SimpleUploadedFile(
            name="image.png",
            content=open("config/media/images/image.png", "rb").read(),
            content_type="image/png",
        )
        response = self.client.post(self.url, self.map)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_a_map_includes_large_image(self):
        self.map["image"] = SimpleUploadedFile(
            name="large_image.png",
            content=open("config/media/images/large_image.png", "rb").read(),
            content_type="image/png",
        )
        response = self.client.post(self.url, self.map)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_maps(self):
        self.client.post(self.url, self.map)

        self.map["name"] = "Another Map"
        self.client.post(self.url, self.map)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_retrieve_a_map(self):
        self.client.post(self.url, self.map)

        response = self.client.get(
            reverse("map-detail", kwargs={"name__iexact": self.map["name"]})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.map["name"])

    def test_retrieve_melee_type_maps(self):
        self.client.post(self.url, self.map)

        another_map = {"name": "Another Map", "type": "top_and_bottom"}
        self.client.post(self.url, another_map)

        response = self.client.get(self.url, {"type": "melee"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_a_map(self):
        self.client.post(self.url, self.map)

        self.map["name"] = "Updated Map"
        response = self.client.put(
            reverse("map-detail", kwargs={"name__iexact": "Sample Map"}), self.map
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_a_map_using_image(self):
        self.client.post(self.url, self.map)

        self.map["image"] = SimpleUploadedFile(
            name="image.png",
            content=open("config/media/images/image.png", "rb").read(),
            content_type="image/png",
        )
        response = self.client.put(
            reverse("map-detail", kwargs={"name__iexact": "Sample Map"}), self.map
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_a_map_using_large_image(self):
        self.client.post(self.url, self.map)

        self.map["image"] = SimpleUploadedFile(
            name="large_image.png",
            content=open("config/media/images/large_image.png", "rb").read(),
            content_type="image/png",
        )
        response = self.client.put(
            reverse("map-detail", kwargs={"name__iexact": "Sample Map"}), self.map
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_a_map(self):
        self.client.post(self.url, self.map)

        response = self.client.delete(
            reverse("map-detail", kwargs={"name__iexact": "Sample Map"}), self.map
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
