from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product


# Create your models here.

# DiscountCode class, represents the DiscountCode entity table
#Discount_types: a list of the two types of discount recongized in our store
#code: the actual code. Must be unique
#discount_type: the type of discount the code will be(percent or fized dollar), this coloumn will only allow the types that exist in DISCOUNT_TYPES
#discount_value: total value of discount
#expriation date
#isactive: indicates if the sale is ative on the store page, defualt is true, if false, sale is not active on the page
#constructor 
class DiscountCode(models.Model):
    DISCOUNT_TYPES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    expiration_date = models.DateTimeField()

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


    #Methods
    #This checks two conditions: the administrator hasn't disabled the code, and the expiration date hasn't passed.
    def is_currently_valid(self):
        return (
            self.active
            and timezone.now() < self.expiration_date
        )

    #calculates the new discount amount. Checks if its either a fixed dollar amount or a percantage discount.
    #validates discount type and applies the approrptiate discount calculation
    def calculate_discount(self, subtotal):
        subtotal = Decimal(subtotal)

        if subtotal < Decimal("0.00"):
            raise ValidationError(
                "Subtotal cannot be negative."
            )

        if not self.is_currently_valid():
            raise ValidationError(
                "Discount code is inactive or expired."
            )

        if self.discount_type == "percentage":
            discount = (
                subtotal
                * self.discount_value
                / Decimal("100")
            )

        elif self.discount_type == "fixed":
            discount = self.discount_value

        else:
            raise ValidationError(
                "Invalid discount type."
            )

        discount = max(
            Decimal("0.00"),
            min(discount, subtotal)
        )

        return discount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    #This prevents negative discount values and percentage discounts greater than 100%.
    def clean(self):
        super().clean()

        if self.discount_value is not None:
            if self.discount_value < Decimal("0.00"):
                raise ValidationError({
                    "discount_value": "Discount cannot be negative."
                })

            if (
                self.discount_type == "percentage"
                and self.discount_value > Decimal("100.00")
            ):
                raise ValidationError({
                    "discount_value": "Percentage cannot exceed 100%."
                })

# Order class, represents the Order entity table
#STATUS_CHOICES: the types of statusus an order has
#user: the specfifc user the order belongs to
#discount_code: foreing key that links a discount code to the order
#created at: attribute to store creation data
#sub_total:Total after product sales, before order discount
#total:	Final amount charged
#discount_amount:Discount code savings
#tax:Sales tax charged
#status:Placed, Completed, or Cancelled
#constructor    
class Order(models.Model):
    STATUS_CHOICES = [
        ("placed", "Placed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    discount_code = models.ForeignKey(
        DiscountCode,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="placed"
    )

    def __str__(self):
        return f"Order #{self.pk} - {self.user}"

# OrderItem class, represents the OrderItem entity table
#Order: Order containing the item. Allows for an order to access all its order items
#product: Product purchased, foreign key links a product with the order item
#quantity: Number of units purchased
#unit_price: unit_price
# PROTECT so an administrator cannot delete a product that is referenced by an existing order.
#Administrators can set Product.is_active = False to remove it from the storefront without destroying order history.
#constructor    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    #Meta class enforces constraints. Quantity of an order item must be at least 1. order and product for an OrderItem must be unqiue
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="order_item_quantity_gte_1"
            ),
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_order_product"
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"




    

