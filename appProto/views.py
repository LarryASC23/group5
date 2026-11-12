from datetime import timedelta
from decimal import Decimal
import json

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from orders.models import Order
from products.models import Product
from products.promotions import current_store_sale


def homepage(request):
    products = (
        Product.objects.filter(is_active=True)
        .prefetch_related("categories", "sales")
        .order_by("name")[:4]
    )
    return render(request, "home.html", {"products": products, "site_sale": current_store_sale()})


def about(request):
    return render(request, "about.html")


def image_credits(request):
    source_file = settings.BASE_DIR / "products" / "image_sources.json"
    with source_file.open(encoding="utf-8") as stream:
        sources = json.load(stream)
    for source in sources:
        if source["license"] == "pdm":
            source["license_label"] = "Public Domain Mark"
        elif source["license"] == "cc0":
            source["license_label"] = "CC0"
        else:
            source["license_label"] = f"CC {source['license'].upper()} {source['license_version']}"
    return render(request, "image_credits.html", {"sources": sources})


@staff_member_required
def staff_dashboard(request):
    last_30_days = timezone.now() - timedelta(days=30)
    recent_sales = Order.objects.filter(created_at__gte=last_30_days).exclude(status="cancelled")
    return render(request, "staff/dashboard.html", {
        "orders_to_fulfill": Order.objects.filter(status="placed").count(),
        "orders_30d": recent_sales.count(),
        "revenue_30d": recent_sales.aggregate(amount=Sum("total"))["amount"] or Decimal("0.00"),
        "active_products": Product.objects.filter(is_active=True).count(),
        "recent_orders": Order.objects.select_related("user").order_by("-created_at")[:8],
        "low_stock_products": Product.objects.filter(is_active=True, quantity__lte=5).order_by("quantity", "name")[:8],
    })

