from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError

# Create your models here.

# Category class, represents the Catagory entity table
#Name: catorgy name
#description: catagory description
#constructor function
class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name

# Product class, represents the Product entity table
#name: name of product
#description: description of product
#price: price of product(usues decimal field)
#quantity: amount of product(must be psotive integer)
#image: loads up product image(tbd on how will we will implment this)
#isactive: indicates if the product is ative on the store page, defualt is true, if false, product is not shown on the page
#categories: creates the many-to-many relationship between product and categories,related_name="products" allows us to retrieve all products belonging to a particular category.
#constructor 
class Product(models.Model):
    name = models.CharField(max_length=200)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    quantity = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to="products/"
    )

    is_active = models.BooleanField(default=True)

    categories = models.ManyToManyField(
        Category,
        related_name="products"
    )

    def __str__(self):
        return self.name

    #usage functions
    
    #if multiple sales apply to a product, we only choose the sale that gives thye biggest discount
    def get_effective_price(self):
        #gets current product price
        lowest_price = self.price
        #iterates throguh all sales associated with the product
        for sale in self.sales.all():
            if sale.is_currently_active():#checks if the sale is active
                sale_price = sale.calculate_price(self.price)#calculates the price after the sale is applied
                #lowest price will be the the min value of all prices calculated
                lowest_price = min(
                    lowest_price,
                    sale_price
                )

        return lowest_price


# Sale class, represents the Sale entity table
#Discount_types: a list of the two types of discount recongized in our store
#name: name of Sale
#products:creates the many-to-many relationship between product and sales,related_name="sales" allows us to retrieve all sales belonging to a particular product.
#discount_type: the type of discount the sale will be(percent or fized dollar), this coloumn will only allow the types that exist in DISCOUNT_TYPES
#discount_value: total value of discount
#sale start date
#sale end date
#isactive: indicates if the sale is ative on the store page, defualt is true, if false, sale is not active on the page
#constructor 
class Sale(models.Model):
    DISCOUNT_TYPES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    name = models.CharField(max_length=100)

    products = models.ManyToManyField(
        Product,
        related_name="sales"
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    #validation functions
    
    #checks if sale is active, if its set to active, returns false, if sale reaches end date, returns false, else function returns true
    def is_currently_active(self):
        now = timezone.now()

        return (
        self.active
        and self.start_date <= now < self.end_date
        )

    #calculates the new price after a discount has been made. Checks if its either a fixed dollar amount or a percantage discount.
    #validates discount type and applies the approrptiate discount calculation
    def calculate_price(self, original_price):
        original_price = Decimal(original_price)

        if self.discount_type == "percentage":
            discount = (
                original_price
                * self.discount_value
                / Decimal("100")
            )

        elif self.discount_type == "fixed":
            discount = self.discount_value

        else:
            raise ValidationError("Invalid discount type.")

        discounted_price = original_price - discount

        return max(
            Decimal("0.00"),
            discounted_price.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        )

    #validates the values pased into the databse for sales. Rejects invalid data
    def clean(self):
        super().clean()
        #checks if there is a dicount value
        if self.discount_value is not None:
            if self.discount_value < Decimal("0.00"):#checks if s sale amount is negative
                raise ValidationError({
                    "discount_value": "Discount cannot be negative."
                })
            #checks if a percnatge discount exceeds 100%
            if (
                self.discount_type == "percentage"
                and self.discount_value > Decimal("100.00")
            ):
                raise ValidationError({
                    "discount_value": "Percentage cannot exceed 100%."
                })
        #checks if the end date is after the start date
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date <= self.start_date
        ):
            raise ValidationError({
                "end_date": "End date must be after start date."
            })



