from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product
from .promotions import current_store_sale


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
    grouped = {}
    for product in products:
        categories = list(product.categories.all())
        category = min(categories, key=lambda item: item.name) if categories else None
        key = category.pk if category else None
        grouped.setdefault(key, []).append(product)

    category_ids = [key for key in grouped if key is not None]
    sections = [
        {"category": category, "products": grouped[category.pk]}
        for category in Category.objects.filter(pk__in=category_ids).order_by("name")
    ]
    if None in grouped:
        sections.append({"category": None, "products": grouped[None]})
    return render(request, "products/products.html", {
        "sections": sections,
        "site_sale": current_store_sale(),
    })


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
