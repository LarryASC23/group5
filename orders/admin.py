from django.contrib import admin
from .models import DiscountCode, Order, OrderItem

# Register your models here.

#This will allow administrators to create and manage discount codes using Django's built-in admin interface
@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "expiration_date",
        "active",
    )

    search_fields = ("code",)
    list_filter = ("discount_type", "active")


#This will allow administrators to manage order information. Will change to read only in the future
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "subtotal",
        "discount_amount",
        "tax",
        "total",
        "status",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
    )

    inlines = [OrderItemInline]


