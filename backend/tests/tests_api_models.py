from django.urls import reverse
from rest_framework.test import APITestCase


class RecipeTests(APITestCase):
    def test_recipe_list(self):
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, 200)
