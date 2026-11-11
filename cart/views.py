from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Cart, CartItem


def return_to(request):
    destination = request.POST.get("next", "")
    if destination and url_has_allowed_host_and_scheme(destination, {request.get_host()}):
        return redirect(destination)
    return redirect("products:list")


def posted_quantity(request):
    try:
        return int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        raise ValidationError("Enter a valid quantity.")


@login_required
@require_POST
def add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    try:
        cart.add_product(product, posted_quantity(request))
        messages.success(request, f"{product.name} added to your cart.")
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    return return_to(request)


@login_required
@require_POST
def update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart.objects.filter(user=request.user).first()
    if cart is None:
        raise Http404
    try:
        cart.update_product_quantity(product, posted_quantity(request))
        messages.success(request, "Cart updated.")
    except (ValidationError, CartItem.DoesNotExist) as exc:
        messages.error(request, exc.messages[0] if isinstance(exc, ValidationError) else "Item not found in your cart.")
    return return_to(request)


@login_required
@require_POST
def remove(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.remove_product(product)
        messages.success(request, "Item removed from your cart.")
    return return_to(request)
