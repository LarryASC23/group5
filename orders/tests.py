from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from cart.models import CartItem
from products.models import Product
from .models import DiscountCode, Order


class StorefrontFlowTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Demo Remedy", description="A fictional product", price=Decimal("10.00"),
            quantity=5, image="products/demo.svg",
        )

    def test_signup_cart_discount_and_checkout(self):
        response = self.client.post("/signup/", {
            "username": "buyer", "email": "buyer@example.test",
            "password1": "StrongPass!482", "password2": "StrongPass!482",
        })
        self.assertRedirects(response, "/account/")
        self.assertEqual(self.client.get(f"/products/{self.product.pk}/").status_code, 200)

        self.client.post(f"/cart/add/{self.product.pk}/", {"quantity": "2"})
        self.assertContains(self.client.get("/checkout/"), "Demo Remedy")
        self.client.post(f"/cart/update/{self.product.pk}/", {"quantity": "1"})
        self.assertEqual(CartItem.objects.get().quantity, 1)

        DiscountCode.objects.create(
            code="TENOFF", discount_type="percentage", discount_value=Decimal("10.00"),
            expiration_date=timezone.now() + timedelta(days=1),
        )
        self.client.post("/checkout/", {"action": "apply_code", "discount_code": "TENOFF"})
        self.assertContains(self.client.get("/checkout/"), "9.74")
        response = self.client.post("/checkout/", {"action": "place_order"})
        order = Order.objects.get()
        self.assertRedirects(response, f"/checkout/complete/{order.pk}/")
        self.assertEqual(order.total, Decimal("9.74"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 4)
        self.assertFalse(CartItem.objects.exists())

        other = User.objects.create_user("other", password="StrongPass!483")
        self.client.force_login(other)
        self.assertEqual(self.client.get(f"/account/orders/{order.pk}/").status_code, 404)
        self.assertEqual(self.client.get(f"/checkout/complete/{order.pk}/").status_code, 404)

    def test_catalog_excludes_inactive_products_and_filters_search(self):
        Product.objects.create(
            name="Hidden Product", description="Not listed", price=Decimal("4.00"),
            quantity=1, image="products/hidden.svg", is_active=False,
        )
        self.assertContains(self.client.get("/products/?q=Remedy"), "Demo Remedy")
        self.assertNotContains(self.client.get("/products/"), "Hidden Product")
        self.assertContains(self.client.get("/"), "Demo Remedy")

    def test_staff_dashboard_requires_staff(self):
        user = User.objects.create_user("member", password="StrongPass!484")
        self.client.force_login(user)
        self.assertEqual(self.client.get("/staff/").status_code, 302)
        user.is_staff = True
        user.save(update_fields=["is_staff"])
        self.assertContains(self.client.get("/staff/"), "Staff overview")
