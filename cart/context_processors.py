from decimal import Decimal, ROUND_HALF_UP

from orders.models import DiscountCode
from orders.services import TAX_RATE
from .models import Cart


def cart_summary(request):
    empty = {
        "cart_items": [], "cart_count": 0,
        "subtotal": Decimal("0.00"), "discount": Decimal("0.00"),
        "tax": Decimal("0.00"), "total": Decimal("0.00"), "discount_code": "",
    }
    if not request.user.is_authenticated:
        return empty

    cart = Cart.objects.filter(user=request.user).first()
    if cart is None:
        return empty

    items = list(cart.items.select_related("product").prefetch_related("product__sales"))
    subtotal = sum((item.get_total_price() for item in items), Decimal("0.00"))
    code_name = request.session.get("checkout_discount_code", "")
    code = DiscountCode.objects.filter(code__iexact=code_name).first() if code_name else None
    discount = Decimal("0.00")
    if code and code.is_currently_valid():
        discount = code.calculate_discount(subtotal)
    else:
        code = None
    tax = ((subtotal - discount) * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "cart_items": items,
        "cart_count": sum(item.quantity for item in items),
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": subtotal - discount + tax,
        "discount_code": code.code if code else "",
    }
