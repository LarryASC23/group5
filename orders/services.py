
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from cart.models import Cart, CartItem
from products.models import Product
from .models import Order, OrderItem, DiscountCode

#sets default tax rate
TAX_RATE = Decimal("0.0825")
CENT = Decimal("0.01")

#decorator wraps the function in a database transaction. This transaction handles the chekout logic
#if any error happens all potential changes to the database are rolled back to their original states
#NOTE: WILL ADD MORE COMMENTS TO THIS CODE
@transaction.atomic
def checkout_cart(cart, discount_code=None):
    # 1. Lock the cart while checkout is processing.
    cart = Cart.objects.select_for_update().get(pk=cart.pk)

    # 2. Retrieve the cart items.
    cart_items = list(
        CartItem.objects.filter(cart=cart)
        .select_related("product")
        .order_by("product_id")
    )

    if not cart_items:
        raise ValidationError("Cannot checkout an empty cart.")

    # 3. Lock the products and verify inventory.
    product_ids = [item.product_id for item in cart_items]

    products = {
        product.pk: product
        for product in Product.objects.select_for_update()
        .filter(pk__in=product_ids)
        .order_by("pk")
    }

    subtotal = Decimal("0.00")
    purchased_items = []

    for item in cart_items:
        product = products.get(item.product_id)

        if product is None or not product.is_active:
            raise ValidationError(
                "A product in your cart is unavailable."
            )

        if item.quantity < 1:
            raise ValidationError("Invalid cart item quantity.")

        if item.quantity > product.quantity:
            raise ValidationError(
                f"Insufficient inventory for {product.name}."
            )

        unit_price = product.get_effective_price()
        line_total = unit_price * item.quantity

        subtotal += line_total

        purchased_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": unit_price,
        })

    # 4. Apply an optional discount code.
    discount_amount = Decimal("0.00")

    if discount_code is not None:
        discount_code = DiscountCode.objects.get(
            pk=discount_code.pk
        )

        discount_amount = discount_code.calculate_discount(
            subtotal
        )

    # 5. Calculate tax and final total.
    discounted_subtotal = subtotal - discount_amount

    tax = (discounted_subtotal * TAX_RATE).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )

    total = discounted_subtotal + tax

    # 6. Create the order.
    order = Order.objects.create(
        user=cart.user,
        discount_code=discount_code,
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax=tax,
        total=total,
        status="placed",
    )

    # 7. Create order items and decrease inventory.
    for purchased in purchased_items:
        product = purchased["product"]
        quantity = purchased["quantity"]

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=purchased["unit_price"],
        )

        updated = Product.objects.filter(
            pk=product.pk,
            quantity__gte=quantity
        ).update(
            quantity=F("quantity") - quantity
        )

        if updated != 1:
            raise ValidationError(
                f"Insufficient inventory for {product.name}."
            )

    # 8. Empty the cart without deleting it.
    CartItem.objects.filter(cart=cart).delete()

    cart.save(update_fields=["updated_at"])

    return order

#this mangement service ensures that status changes are handledle gracfully and data regarding it is accurate 
#If one inventory update fails, we don't want an order marked as cancelled while only some of its products have been restocked.
#The transaction ensures that either all database changes succeed or none are committed.
#Cancelled/Completed status cannot be changed
#this function updates a product's inventory quantity and changes the status of an order.
#NOTE: if an order is placed it uodates the cart products quantity, complete status does change product quantity
#returns an order object with the updated order
@transaction.atomic
def update_order_status(order, new_status):
    if new_status not in ("completed", "cancelled"):
        raise ValidationError("Invalid target order status.")

    # Lock the order to prevent simultaneous status updates.
    order = Order.objects.select_for_update().get(
        pk=order.pk
    )

    if order.status != "placed":
        raise ValidationError(
            "Only placed orders can change status."
        )

    if new_status == "cancelled":
        order_items = list(
            order.items.order_by("product_id")
        )

        # Lock product rows in a consistent order.
        product_ids = [
            item.product_id for item in order_items
        ]

        products = list(
            Product.objects.select_for_update()
            .filter(pk__in=product_ids)
            .order_by("pk")
        )

        if len(products) != len(set(product_ids)):
            raise ValidationError(
                "An order product could not be found."
            )
        #uodates the quantity of all products in the cart if the transactionj is set to cancelled
        for item in order_items:
            Product.objects.filter(
                pk=item.product_id
            ).update(
                quantity=F("quantity") + item.quantity
            )

    order.status = new_status
    order.save(update_fields=["status"])

    return order



#Databse is 95% complete id say
#7. A few important considerations
#Before integrating checkout into the website, there are several details we'll want to address.

#Concurrent cart modifications: The checkout function locks the cart record, but other code modifying cart items must follow the same locking convention. We'll coordinate those operations when connecting the service to the frontend, particularly when switching to PostgreSQL.

#Repeated checkout requests: We'll eventually need protection against accidentally submitting the same checkout request twice. A unique checkout request identifier is a common way to prevent duplicate orders.

#Historical records: Our OrderItem stores the purchased unit price, but the product's name and description still come from the current Product record. We may want to store a product-name snapshot as well.

#Order statuses: Checkout creates an order with status Placed. We'll implement the separate administrative workflow for changing it to Completed or Cancelled, including rules for terminal statuses.

#Tax: We're using the project's specified 8.25% rate and calculating it after discounts. This is suitable for the agreed class-project calculation; actual tax rules can be more complex.
#The next step will be implementing order status management and tightening the checkout workflow, before we begin building Django views and templates for the customer-facing website.