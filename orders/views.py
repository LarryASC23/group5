from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from cart.models import Cart
from .models import DiscountCode, Order
from .services import checkout_cart


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    discount_error = ""
    saved_code = request.session.get("checkout_discount_code", "")
    if saved_code:
        active_code = DiscountCode.objects.filter(code__iexact=saved_code).first()
        if active_code is None or not active_code.is_currently_valid():
            request.session.pop("checkout_discount_code", None)
            messages.warning(request, "Your discount code expired or is no longer available.")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "remove_code":
            request.session.pop("checkout_discount_code", None)
            return redirect("checkout")

        if action == "apply_code":
            request.session.pop("checkout_discount_code", None)
            entered = request.POST.get("discount_code", "").strip()
            code = DiscountCode.objects.filter(code__iexact=entered).first() if entered else None
            if code and code.is_currently_valid():
                try:
                    code.calculate_discount(cart.get_subtotal() if cart else 0)
                except ValidationError as exc:
                    discount_error = exc.messages[0]
                else:
                    request.session["checkout_discount_code"] = code.code
                    messages.success(request, "Discount code applied.")
                    return redirect("checkout")
            else:
                discount_error = "This discount code is invalid or expired."

        elif action == "place_order":
            if cart is None:
                messages.error(request, "Your cart is empty.")
                return redirect("checkout")
            code_name = request.session.get("checkout_discount_code", "")
            code = DiscountCode.objects.filter(code__iexact=code_name).first() if code_name else None
            try:
                order = checkout_cart(cart, code)
            except ValidationError as exc:
                messages.error(request, exc.messages[0])
            else:
                request.session.pop("checkout_discount_code", None)
                return redirect("checkout_complete", pk=order.pk)
        elif action != "apply_code":
            messages.error(request, "Unknown checkout action.")

    return render(request, "checkout/checkout.html", {"discount_error": discount_error})


@login_required
def complete(request, pk):
    order = get_object_or_404(
        Order.objects.filter(user=request.user).select_related("discount_code").prefetch_related("items__product"),
        pk=pk,
    )
    return render(request, "checkout/complete.html", {"order": order})
