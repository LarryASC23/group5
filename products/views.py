from django.shortcuts import render

# Create your views here.
def products(request):
    return render(request, 'products/products.html')  # Render the product.html template when the product_list view is accessed.