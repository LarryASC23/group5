from django.db import models
from django.conf import settings
from products.models import Product
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from decimal import Decimal

# Create your models here.

# Cart class, represents the Cart entity table
#user: creates a one to one relationship between cart and user. usus django's built in user authethication.
#if a user is deleted so is the cart
#created_at: saves time of creation
#updated_at: saves time when cart record is saved
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Cart belonging to {self.user.username}"

    #methods

    #method that adds products to the cart. This methods creates a cartItem that corresponds to a product
    #Note adding to cartwill not decrease inventory, intevtory reducing when customer checks out
    #has methods for check is user adds more of a product than whats available
    def add_product(self, product, quantity=1):
        if quantity < 1:
            raise ValidationError(
                "Quantity must be at least 1."
            )

        with transaction.atomic():
            product = Product.objects.select_for_update().get(
                pk=product.pk
            )

            if not product.is_active:
                raise ValidationError(
                    "This product is not available."
                )

            item = CartItem.objects.select_for_update().filter(
                cart=self,
                product=product
            ).first()

            current_quantity = item.quantity if item else 0
            new_quantity = current_quantity + quantity

            if new_quantity > product.quantity:
                raise ValidationError(
                    "Requested quantity exceeds available inventory."
                )

            if item:
                item.quantity = new_quantity
                item.save(update_fields=["quantity"])
            else:
                item = CartItem.objects.create(
                    cart=self,
                    product=product,
                    quantity=new_quantity
                )

            self.save(update_fields=["updated_at"])

        return item

    #method that lets customers change the quantity of an item already in their cart.
    #Setting the quantity to zero removes the item entirely.
    def update_product_quantity(self, product, quantity):
        if quantity < 0:
            raise ValidationError(
                "Quantity cannot be negative."
            )

        with transaction.atomic():
            item = CartItem.objects.select_for_update().get(
                cart=self,
                product=product
            )

            if quantity == 0:
                item.delete()

            else:
                product = Product.objects.select_for_update().get(
                    pk=product.pk
                )

                if not product.is_active:
                    raise ValidationError(
                        "This product is not available."
                    )

                if quantity > product.quantity:
                    raise ValidationError(
                        "Requested quantity exceeds available inventory."
                    )

                item.quantity = quantity
                item.save(update_fields=["quantity"])

            self.save(update_fields=["updated_at"])

    #removes an item from the cart
    #if  no item in the cart, this method has no effect
    def remove_product(self, product):
        deleted, _ = self.items.filter(
            product=product
        ).delete()

        if deleted:
            self.save(update_fields=["updated_at"])

    #gets the subtotal for all cart items in the cart
    def get_subtotal(self):
        subtotal = Decimal("0.00")

        for item in self.items.select_related("product"):
            subtotal += item.get_total_price()

        return subtotal

# Cart class, represents the Cart entity table(the actual product inside the cart)
#cart: foreign key to a Cart, links CartItem to a cart, a cart can have many cart items.related_name="items" lets us retrive all items belonging to a cart
#product:foreign key that links the CartItem to a product. Associates a cartitem to a product
#Meta Class: defines constraints
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )
    #defines constraints
    class Meta:
        #contraints prevents duplicate entries for the same product within a single car and enforces a minimum quantity of 1 at the database level.
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="cart_item_quantity_gte_1"
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    #methods
    #This gets the total price of an cart item
    #method will reuse the get_effective_price() methodin the Product Class. cart automatically accounts for active product sales.
    #multiplies effective price by the quantity of the product in the cart. 
    def get_total_price(self):
        return self.product.get_effective_price() * self.quantity


