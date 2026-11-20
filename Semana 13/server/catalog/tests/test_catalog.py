import io

from django.contrib import admin as django_admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image

from catalog.models import Category, Product
from quiz.tests.helpers import reader_token

_buffer = io.BytesIO()
Image.new("RGB", (2, 2), (255, 255, 255)).save(_buffer, "PNG")
PNG_BYTES = _buffer.getvalue()


class CatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.token = reader_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")
        self.drinks = Category.objects.create(
            name="Drinks", description="Bebidas frías y calientes."
        )
        self.tech = Category.objects.create(
            name="Technology", description="Accesorios de escritorio."
        )
        self.coffee = self.make_product("Coffee", self.drinks, "10.50", 20)
        self.mouse = self.make_product("Mouse", self.tech, "45.00", 5)

    def make_product(self, name, category, price, stock):
        return Product.objects.create(
            name=name,
            category=category,
            description=f"Descripción de {name}.",
            price=price,
            stock=stock,
            image=SimpleUploadedFile(
                f"{name.lower()}.png", PNG_BYTES, content_type="image/png"
            ),
        )

    def test_product_list_returns_nested_category_in_one_request(self):
        response = self.client.get("/api/catalog/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first = response.data["results"][0]
        self.assertIn("category", first)
        self.assertIn(first["category"]["name"], ["Drinks", "Technology"])
        self.assertIn("description", first["category"])
        self.assertIn("product_count", first["category"])
        self.assertNotIsInstance(first["category"], int)

    def test_image_url_is_absolute_for_the_browser(self):
        response = self.client.get("/api/catalog/products/")
        self.assertTrue(response.data["results"][0]["image_url"].startswith("http"))

    def test_filter_by_category(self):
        response = self.client.get(f"/api/catalog/products/?category={self.tech.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, ["Mouse"])

    def test_create_product_with_write_only_category_id(self):
        payload = {
            "name": "Keyboard",
            "description": "Teclado compacto.",
            "price": "129.00",
            "stock": 7,
            "category_id": self.tech.id,
            "image": SimpleUploadedFile("keyboard.png", PNG_BYTES, content_type="image/png"),
        }
        response = self.client.post("/api/catalog/products/", payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category"]["name"], "Technology")
        self.assertTrue(Product.objects.filter(name="Keyboard", category=self.tech).exists())

    def test_update_product(self):
        payload = {
            "name": "Coffee premium",
            "description": "Tueste oscuro.",
            "price": "12.90",
            "stock": 33,
            "category_id": self.drinks.id,
        }
        response = self.client.put(
            f"/api/catalog/products/{self.coffee.id}/", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.coffee.refresh_from_db()
        self.assertEqual(str(self.coffee.price), "12.90")
        self.assertEqual(self.coffee.stock, 33)

    def test_delete_product(self):
        response = self.client.delete(f"/api/catalog/products/{self.mouse.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.mouse.id).exists())

    def test_category_endpoints_work(self):
        response = self.client.get("/api/catalog/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        created = self.client.post(
            "/api/catalog/categories/",
            {"name": "Home", "description": "Artículos del hogar."},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="Home").exists())

    def test_catalog_is_public_in_the_classroom_lab(self):
        anonymous = APIClient()
        response = anonymous.get("/api/catalog/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CatalogAdminTests(TestCase):
    def test_both_models_are_registered_with_listings_and_filters(self):
        self.assertIn(Category, django_admin.site._registry)
        self.assertIn(Product, django_admin.site._registry)
        product_admin = django_admin.site._registry[Product]
        self.assertIn("category", product_admin.list_filter)
        self.assertIn("name", product_admin.search_fields)
        self.assertIn("price", product_admin.list_display)
