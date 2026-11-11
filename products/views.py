from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Product


def products(request):
    queryset = Product.objects.filter(is_active=True).prefetch_related("categories", "sales")
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(categories__name__icontains=query)
        ).distinct()

    sort = request.GET.get("sort", "")
    if sort in ("price_asc", "price_desc"):
        products = list(queryset)
        products.sort(key=lambda product: product.get_effective_price(), reverse=sort == "price_desc")
    elif sort == "stock":
        products = queryset.order_by("-quantity", "name")
    else:
        products = queryset.order_by("name")
    return render(request, "products/products.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.filter(is_active=True).prefetch_related("categories", "sales"),
        pk=pk,
    )
    category_ids = [category.pk for category in product.categories.all()]
    related = Product.objects.filter(is_active=True).exclude(pk=pk)
    if category_ids:
        related = related.filter(categories__pk__in=category_ids).distinct()
    related = related.prefetch_related("categories", "sales").order_by("name")[:4]
    return render(request, "products/product_detail.html", {"product": product, "related_products": related})
