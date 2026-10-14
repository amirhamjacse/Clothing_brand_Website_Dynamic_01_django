from django.contrib import admin
from store.models import Category, Product, ProductVariant, ProductImage, Coupon, Order, OrderItem, Review

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'slug', 'is_featured', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'regular_price', 'discount_price', 'stock', 'is_active', 'is_eid_special')
    list_filter = ('category', 'gender', 'is_active', 'is_eid_special', 'is_bestseller')
    search_fields = ('name', 'sku', 'description', 'fabric')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('regular_price', 'discount_price', 'stock', 'is_active')
    inlines = [ProductVariantInline, ProductImageInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_sku', 'size', 'color', 'price', 'quantity', 'subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'total_amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'delivery_area')
    search_fields = ('order_number', 'full_name', 'phone', 'trx_id')
    inlines = [OrderItemInline]

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'min_spend', 'max_discount', 'is_active')
    list_editable = ('is_active',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'city', 'rating', 'created_at')
