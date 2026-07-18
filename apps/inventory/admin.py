from django.contrib import admin
from .models import Category, Product, StockMovement, Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'quantity', 'price', 'category', 'is_low_stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku', 'barcode', 'description')
    readonly_fields = ('created_at', 'updated_at', 'is_low_stock', 'profit_margin')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'barcode', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'cost')
        }),
        ('Stock', {
            'fields': ('quantity', 'min_stock_level')
        }),
        ('Additional', {
            'fields': ('description', 'image', 'is_active')
        }),
        ('Read-only', {
            'fields': ('created_at', 'updated_at', 'is_low_stock', 'profit_margin'),
            'classes': ('collapse',)
        })
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_change', 'reason', 'performed_by', 'timestamp')
    list_filter = ('reason', 'timestamp')
    search_fields = ('product__name', 'product__sku', 'notes')
    readonly_fields = ('timestamp',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sold_by', 'total_amount', 'payment_method', 'sale_date')
    list_filter = ('payment_method', 'sale_date')
    search_fields = ('sold_by__email', 'sold_by__first_name', 'sold_by__last_name', 'notes')
    readonly_fields = ('sale_date', 'created_at', 'updated_at')
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('sale__sale_date',)
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('total_price',)
