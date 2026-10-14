import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

def make_clean_slug(model_class, text, sku='', instance=None):
    base = slugify(text)
    if not base or not base.strip('-'):
        # Bengali or non-ASCII text
        unicode_slug = slugify(text, allow_unicode=True)
        if unicode_slug and unicode_slug.strip('-'):
            base = unicode_slug
        elif sku:
            base = slugify(sku)
        else:
            rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            base = f"item-{rand}"

    slug = base
    counter = 1
    qs = model_class.objects.filter(slug=slug)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.exists():
        slug = f"{base}-{counter}"
        counter += 1
        qs = model_class.objects.filter(slug=slug)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
    return slug


class Category(models.Model):
    GENDER_CHOICES = [
        ('all', 'All / Unisex'),
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='all')
    description = models.TextField(blank=True)
    image = models.CharField(max_length=500, blank=True, help_text="Image URL or relative path")
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug or self.slug.strip('-') == '':
            self.slug = make_clean_slug(Category, self.name, instance=self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"


class Product(models.Model):
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
        ('unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True, allow_unicode=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='men')
    fabric = models.CharField(max_length=150, default='100% Premium Combed Cotton')
    description = models.TextField()
    features = models.TextField(blank=True, help_text="One bullet per line: collar, cut, fitting, care instructions")
    
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    primary_image = models.CharField(max_length=500, help_text="Main product image URL")
    hover_image = models.CharField(max_length=500, blank=True, help_text="Hover / Alternate image URL")
    
    stock = models.PositiveIntegerField(default=20)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_eid_special = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    rating_count = models.PositiveIntegerField(default=18)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug or self.slug.strip('-') == '':
            self.slug = make_clean_slug(Product, self.name, sku=self.sku, instance=self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ৳{self.get_price()}"

    def get_price(self):
        if self.discount_price and self.discount_price > 0:
            return self.discount_price
        return self.regular_price

    def has_discount(self):
        return bool(self.discount_price and self.discount_price < self.regular_price)

    def discount_percent(self):
        if self.has_discount():
            diff = self.regular_price - self.discount_price
            return int((diff / self.regular_price) * 100)
        return 0

    def in_stock(self):
        return self.stock > 0

    def get_features_list(self):
        if not self.features:
            return []
        return [f.strip() for f in self.features.split('\n') if f.strip()]


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=20, default='40')
    color = models.CharField(max_length=50, default='Default')
    color_code = models.CharField(max_length=10, default='#111827', help_text="Hex color code for swatch")
    stock = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} | Size: {self.size} | Color: {self.color}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.CharField(max_length=500)
    caption = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):
    code = models.CharField(max_length=25, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery (ক্যাশ অন ডেলিভারি)'),
        ('bkash', 'bKash (বিকাশ)'),
        ('nagad', 'Nagad (নগদ)'),
        ('rocket', 'Rocket (রকেট)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending (অপেক্ষমান)'),
        ('confirmed', 'Confirmed (নিশ্চিত)'),
        ('processing', 'Processing (প্রস্তুত হচ্ছে)'),
        ('shipped', 'Shipped (কুরিয়ারে হস্তান্তর)'),
        ('delivered', 'Delivered (ডেলিভার সম্পন্ন)'),
        ('cancelled', 'Cancelled (বাতিল)'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    DELIVERY_AREA_CHOICES = [
        ('inside_dhaka', 'Inside Dhaka (ঢাকা সিটি) - ৳60'),
        ('outside_dhaka', 'Outside Dhaka (ঢাকার বাইরে সারা বাংলাদেশ) - ৳120'),
    ]

    order_number = models.CharField(max_length=30, unique=True, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    
    # Customer Details
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    division = models.CharField(max_length=50, default='Dhaka')
    district = models.CharField(max_length=50, default='Dhaka')
    delivery_address = models.TextField()
    customer_notes = models.TextField(blank=True)
    
    # Delivery & Totals
    delivery_area = models.CharField(max_length=20, choices=DELIVERY_AREA_CHOICES, default='inside_dhaka')
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=60.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon_code = models.CharField(max_length=25, blank=True)

    # Payment
    payment_method = models.CharField(max_length=15, choices=PAYMENT_CHOICES, default='cod')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    sender_number = models.CharField(max_length=20, blank=True, help_text="bKash/Nagad sender phone number")
    trx_id = models.CharField(max_length=60, blank=True, help_text="Transaction ID (TrxID)")

    # Status & Logistics
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    courier_tracking_id = models.CharField(max_length=100, blank=True, help_text="e.g. Steadfast, Pathao, RedX tracking")
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            rand_str = ''.join(random.choices(string.digits, k=5))
            self.order_number = f"AHMZ-{rand_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.full_name} (৳{self.total_amount})"

    def status_color(self):
        colors = {
            'pending': 'amber',
            'confirmed': 'blue',
            'processing': 'indigo',
            'shipped': 'purple',
            'delivered': 'emerald',
            'cancelled': 'rose',
        }
        return colors.get(self.status, 'gray')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.size})"


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50, default='Dhaka')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    is_verified_buyer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} on {self.product.name} ({self.rating}★)"
