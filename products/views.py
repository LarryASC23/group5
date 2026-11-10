from django.shortcuts import render
from django.db.models import Q
from .models import Product

def products(request):
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        "categories", "sales"
    )

    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(categories__name__icontains=query)
        ).distinct()

    sort = request.GET.get("sort", "")
    if sort == "price_asc":
        queryset = queryset.order_by("price", "name")
    elif sort == "price_desc":
        queryset = queryset.order_by("-price", "name")
    elif sort == "stock":
        queryset = queryset.order_by("-quantity", "name")
    else:
        queryset = queryset.order_by("name")

    return render(request, "products/products.html", {"products": queryset})
