#views.py file for loading pages in the django project. 
#from django.http import HttpResponse
from django.shortcuts import render
from products.models import Product

def homepage(request):
    products = (
        Product.objects.filter(is_active=True)
        .prefetch_related("categories", "sales")
        .order_by("name")
    )
    return render(request, "home.html", {"products": products})
def about(request):
    return render(request, "about.html")

