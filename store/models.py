from django.db import models
from django.utils import timezone
from django.utils.html import format_html


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('ALMIRAH', 'Almirah'),
        ('COOLER', 'Cooler'),
        ('TRUNK', 'Trunk'),
        ('STAND', 'Stand'),
    ]

    STOCK_STATUS_CHOICES = [
        ('In Stock', 'In Stock'),
        ('Out of Stock', 'Out of Stock'),
    ]

    BADGE_CHOICES = [
        ('New Arrival', 'New Arrival'),
        ('Best Seller', 'Best Seller'),
        ('Limited Edition', 'Limited Edition'),
        ('', 'None'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    tagline = models.CharField(
        max_length=120,
        blank=True,
        help_text='Optional product tagline displayed on product cards.',
    )
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    discount_percent = models.PositiveIntegerField(
        default=0,
        help_text='Enter discount percentage, e.g. 10 for 10% off. Leave 0 for no discount.',
    )
    stock_status = models.CharField(
        max_length=20,
        choices=STOCK_STATUS_CHOICES,
        default='In Stock',
        help_text='Set the availability status for this product.',
    )
    badge = models.CharField(
        max_length=20,
        choices=BADGE_CHOICES,
        blank=True,
        default='',
        help_text='Promotional badge for the product.',
    )
    available_colors = models.CharField(
        max_length=200,
        blank=True,
        help_text='Comma-separated list of available colors. Example: Black, Silver, #F2C94C',
    )
    dimensions = models.CharField(
        max_length=80,
        blank=True,
        help_text='Product dimensions, e.g. 1630x915x530 mm.',
    )
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=120, blank=True)
    meta_description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    featured_offer = models.BooleanField(default=False, help_text='Display this product in the Special Offer section on the homepage.')
    featured_popular = models.BooleanField(default=False, help_text='Display this product in the Popular Models section on the homepage.')
    featured_homepage_almirah = models.BooleanField(default=False, help_text='Show this Almirah in the Almirah homepage section.')
    featured_homepage_cooler = models.BooleanField(default=False, help_text='Show this Cooler in the Cooler homepage section.')
    featured_homepage_trunk = models.BooleanField(default=False, help_text='Show this Trunk in the Trunk homepage section.')
    featured_homepage_stand = models.BooleanField(default=False, help_text='Show this Stand in the Stand homepage section.')
    featured_homepage = models.BooleanField(default=False, help_text='Legacy homepage flag; use the category-specific homepage fields instead.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_status == 'In Stock' and self.stock_quantity > 0

    @property
    def discount_badge(self):
        return f"{self.discount_percent}% OFF" if self.discount_percent else ''

    @property
    def color_options(self):
        if not self.available_colors:
            return []
        return [color.strip() for color in self.available_colors.split(',') if color.strip()]

    def save(self, *args, **kwargs):
        # Auto-calculate price based on MRP and discount_percent
        if self.mrp > 0:
            from decimal import Decimal
            if self.discount_percent and self.discount_percent > 0:
                discount_amount = (self.mrp * Decimal(self.discount_percent)) / Decimal(100)
                self.price = self.mrp - discount_amount
            else:
                self.price = self.mrp

        if self.stock_quantity <= 0:
            self.stock_status = 'Out of Stock'
        elif self.stock_status == 'Out of Stock' and self.stock_quantity > 0:
            self.stock_status = 'In Stock'
        super().save(*args, **kwargs)


class SliderImage(models.Model):
    caption = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to='slider/')
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order']
        verbose_name = 'Slider Image'
        verbose_name_plural = 'Slider Images'

    def __str__(self):
        return self.caption or f"Slider Image {self.pk}"


class SerialNumberRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    serial_number = models.CharField(max_length=120, unique=True)
    customer_name = models.CharField(max_length=120)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField()
    technician_name = models.CharField(max_length=120, blank=True)
    product_checker_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = 'Serial Number Record'
        verbose_name_plural = 'Serial Number Records'

    def __str__(self):
        return self.serial_number

    @property
    def warranty_valid(self):
        return self.warranty_expiry >= timezone.localdate()


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Process', 'In Process'),
        ('Resolved', 'Resolved'),
    ]

    PRODUCT_CHOICES = [
        ('Almirah', 'Almirah'),
        ('Cooler', 'Cooler'),
        ('Stand', 'Stand'),
        ('Trunk', 'Trunk'),
        ('Other', 'Other'),
    ]

    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    product_type = models.CharField(max_length=50, choices=PRODUCT_CHOICES)
    serial_number = models.CharField(max_length=120, db_index=True)
    bill_copy = models.ImageField(upload_to='complaints/bills/')
    technician_name = models.CharField(max_length=120, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'

    def __str__(self):
        return f"{self.customer_name} | {self.product_type} | {self.serial_number}"

    def bill_preview(self):
        if self.bill_copy:
            return format_html(
                '<img src="{}" width="120" style="object-fit:contain;" />',
                self.bill_copy.url,
            )
        return '(No bill uploaded)'
    bill_preview.short_description = 'Bill Copy Preview'


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]

    DELIVERY_STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    product_details = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='Booked')
    order_date = models.DateField(default=timezone.localdate)
    expected_delivery_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"

    @property
    def is_paid(self):
        return self.payment_status == 'Success'

    def reduce_stock(self):
        if not self.product:
            raise ValueError('Order has no associated product.')
        if self.product.stock_quantity < self.quantity:
            raise ValueError('Insufficient stock to complete the order.')

        self.product.stock_quantity -= self.quantity
        if self.product.stock_quantity <= 0:
            self.product.stock_status = 'Out of Stock'
        self.product.save(update_fields=['stock_quantity', 'stock_status'])


class HomepageBanner(models.Model):
    title = models.CharField(max_length=140)
    subtitle = models.CharField(max_length=240, blank=True)
    image = models.ImageField(upload_to='banners/')
    link_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Homepage Banner'
        verbose_name_plural = 'Homepage Banners'

    def __str__(self):
        return self.title


class Review(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('ALMIRAH', 'Almirah'),
        ('COOLER', 'Cooler'),
        ('TRUNK', 'Trunk'),
        ('STAND', 'Stand'),
        ('OTHER', 'Other'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=120)
    reviewer_email = models.EmailField()
    product_type = models.CharField(max_length=30, choices=PRODUCT_TYPE_CHOICES, default='ALMIRAH')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.reviewer_name} on {self.product.name}"


class ContactSubmission(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'

    def __str__(self):
        return f"{self.name} — {self.subject[:48]}"
