from django.contrib import admin
from .models import Category, Product

# Register your models here.

#This will let us create products, assign multiple categories, search the catalog, and manage inventory through Django Admin.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "quantity",
        "is_active"
    )

    search_fields = ("name", "description")
    list_filter = ("categories", "is_active")
    filter_horizontal = ("categories",)