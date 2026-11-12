from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from .models import Category, Product
from .promotions import current_store_sale


class CuratedCatalogTests(TestCase):
    fixtures = ["demo_catalog.json"]

    def test_every_public_product_has_the_twenty_percent_sale(self):
        with patch("django.utils.timezone.now", return_value=datetime(2026, 11, 12, tzinfo=timezone.utc)):
            products = list(Product.objects.filter(is_active=True))
            self.assertEqual(len(products), 17)
            sale = current_store_sale()
            self.assertIsNotNone(sale)
            self.assertEqual(sale.discount_value, Decimal("20.00"))
            for product in products:
                self.assertEqual(product.get_effective_price(), sale.calculate_price(product.price))

            self.assertContains(self.client.get("/"), "20% off")
            self.assertContains(self.client.get("/products/"), "20% off")
            self.assertNotContains(self.client.get("/about/"), "20% off")

    def test_shop_shows_a_header_for_each_category(self):
        response = self.client.get("/products/")
        self.assertContains(response, "DEPARTMENT 01")
        for category in Category.objects.all():
            self.assertContains(response, category.name)
            self.assertContains(response, category.description)

        filtered = self.client.get("/products/?q=Hemp")
        self.assertContains(filtered, "Hemp Field Print")
        self.assertNotContains(filtered, "Vintage Slot Machine")

    def test_every_listing_has_a_local_image(self):
        missing = [
            product.image.name
            for product in Product.objects.filter(is_active=True)
            if not (settings.MEDIA_ROOT / product.image.name).is_file()
        ]
        self.assertEqual(missing, [])
