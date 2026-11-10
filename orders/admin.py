from django.contrib import admin, messages
from .models import DiscountCode, Order, OrderItem
from django.core.exceptions import ValidationError
from .services import update_order_status

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


#This will allow administrators to manage order information. Admins may not change product, quantity, and unit_price directly
#IE no admin can change financial fields
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "unit_price",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

#makes it so that admins canot directly change the fields of an order. Any admin must use the update_order_status() method to change an order status
#Order admin includes function that allow admins to cancel or complete specfifc orders easily
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

    list_filter = ("status", "created_at")
    search_fields = ("user__username",)

    readonly_fields = (
        "user",
        "discount_code",
        "created_at",
        "subtotal",
        "discount_amount",
        "tax",
        "total",
        "status",
    )

    def has_add_permission(self, request):
        return False

    #prevent administrators from deleting orders through Django Admin.

    #method disables deletion through the order detail page.
    def has_delete_permission(self, request, obj=None):
        return False

    #method explicitly removes Django's bulk deletion action, if present.
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions


    #method allows admins to conviently mark orders as completed. If one order cannot be completed, the action continues processing the remaining orders.
    @admin.action(description="Mark selected orders as completed")
    def mark_completed(self, request, queryset):
        success_count = 0
        failed_count = 0
        #queryset contains the orders selected by the administrator.
        for order in queryset:
            try: #function checks whether the transition is allowed
                update_order_status(order, "completed")
                success_count += 1
            except ValidationError:
                failed_count += 1

        if success_count:
            self.message_user(
                request,
                f"{success_count} order(s) marked as completed.",
                level=messages.SUCCESS,
            )

        if failed_count:
            self.message_user(
                request,
                f"{failed_count} order(s) could not be completed.",
                level=messages.WARNING,
            )

    #method allows admins to conviently mark orders as cancelled. If one order cannot be cancelled, the action continues processing the remaining orders.
    @admin.action(description="Cancel selected orders and restore inventory")
    def cancel_orders(self, request, queryset):
        success_count = 0
        failed_count = 0

        for order in queryset:
            try:#function checks whether the transition is allowed
                update_order_status(order, "cancelled")
                success_count += 1
            except ValidationError:
                failed_count += 1

        if success_count:
            self.message_user(
                request,
                f"{success_count} order(s) cancelled and restocked.",
                level=messages.SUCCESS,
            )

        if failed_count:
            self.message_user(
                request,
                f"{failed_count} order(s) could not be cancelled.",
                level=messages.WARNING,
            )

    inlines = [OrderItemInline]
    #displays option for admins to chnage order status
    actions = [
        "mark_completed",
        "cancel_orders",
    ]


