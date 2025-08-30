from django.db import models
from django.contrib.postgres.fields import ArrayField

# Store Configuration
class StoreConfiguration(models.Model):
    STORE_TYPES = [
        ('buffet', 'Buffet'),
        ('clothing', 'Clothing'),
        ('equipment', 'Equipment'),
        ('supplements', 'Supplements'),
    ]

    gym_id = models.CharField(max_length=100)
    store_type = models.CharField(max_length=50, choices=STORE_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict)  # currency, tax_percentage, etc.

    def __str__(self):
        return self.name

# Categories
class Category(models.Model):
    store = models.ForeignKey(StoreConfiguration, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=50)
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    parent_category = models.ForeignKey(
        'self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subcategories'
    )

    def __str__(self):
        return self.name

# Products
class Product(models.Model):
    store = models.ForeignKey(StoreConfiguration, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    images = ArrayField(models.URLField(), blank=True, default=list)
    sku = models.CharField(max_length=100, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(blank=True, null=True)
    min_stock_level = models.IntegerField(blank=True, null=True)
    max_quantity_per_order = models.IntegerField(blank=True, null=True)
    preparation_time = models.IntegerField(blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    nutritional_info = models.JSONField(default=dict)  # protein, carbs, fat, etc.
    allergens = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    size_variants = models.JSONField(default=list)
    color_variants = models.JSONField(default=list)
    is_featured = models.BooleanField(default=False)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_start_date = models.DateTimeField(blank=True, null=True)
    discount_end_date = models.DateTimeField(blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
    ]

    orderId = models.CharField(
        max_length=100, null=True)

    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    qrcode = models.CharField(max_length=255, blank=True, null=True)

    customer_name = models.CharField(max_length=255, blank=True, null=True, default='')
    customer_phone = models.CharField(max_length=20, blank=True, null=True, default='')

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        blank=True,
        null=True,
        default='cash'
    )
    
    note = models.TextField(blank=True, null=True, default='')

    def __str__(self):
        return f"Order {self.orderId} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.CharField(max_length=100, blank=True, null=True, default='')
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    def __str__(self):
        return f"{self.quantity} x {self.name or 'Unknown'} (Order {self.order.orderId})"
