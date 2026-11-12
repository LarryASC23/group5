from django.db.models import Count, Q
from django.utils import timezone

from .models import Product, Sale


def current_store_sale():
    """Return an active percentage sale only when it covers the entire public catalog."""
    active_count = Product.objects.filter(is_active=True).count()
    if active_count == 0:
        return None
    now = timezone.now()
    return (
        Sale.objects.filter(
            active=True,
            discount_type="percentage",
            start_date__lte=now,
            end_date__gt=now,
        )
        .annotate(active_product_count=Count("products", filter=Q(products__is_active=True), distinct=True))
        .filter(active_product_count=active_count)
        .order_by("-discount_value", "pk")
        .first()
    )
