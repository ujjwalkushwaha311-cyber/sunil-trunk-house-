import csv
from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Complaint,
    ContactSubmission,
    HomepageBanner,
    Order,
    Product,
    Review,
    SerialNumberRecord,
    SliderImage,
)


_original_each_context = admin.site.each_context

def each_context(request):
    context = _original_each_context(request)
    context['unresolved_complaint_count'] = Complaint.objects.filter(status__in=['Pending', 'In Process']).count()
    return context

admin.site.each_context = each_context


def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)
    field_names = [field.name for field in meta.fields]
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response

export_as_csv.short_description = 'Export selected records to CSV'


class SuperuserOnlyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class ComplaintStaffAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)

    def has_add_permission(self, request):
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)


@admin.register(Product)
class ProductAdmin(ComplaintStaffAdmin):
    list_display = (
        'name',
        'category',
        'tagline',
        'mrp',
        'price',
        'discount_percent',
        'dimensions',
        'stock_quantity',
        'stock_status',
        'badge',
        'featured_offer',
        'featured_popular',
        'featured_homepage_almirah',
        'featured_homepage_cooler',
        'featured_homepage_trunk',
        'featured_homepage_stand',
        'created_at',
    )
    list_editable = (
        'tagline',
        'mrp',
        'price',
        'discount_percent',
        'dimensions',
        'stock_quantity',
        'stock_status',
        'badge',
        'featured_offer',
        'featured_popular',
        'featured_homepage_almirah',
        'featured_homepage_cooler',
        'featured_homepage_trunk',
        'featured_homepage_stand',
    )
    list_filter = (
        'category',
        'stock_status',
        'badge',
        'featured_offer',
        'featured_popular',
        'featured_homepage_almirah',
        'featured_homepage_cooler',
        'featured_homepage_trunk',
        'featured_homepage_stand',
    )
    search_fields = ('name', 'tagline', 'meta_title', 'meta_description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'category', 'tagline', 'price', 'image', 'description'),
        }),
        ('Inventory & Promotion', {
            'fields': ('stock_quantity', 'mrp', 'discount_percent', 'dimensions', 'available_colors', 'stock_status', 'badge', 'featured_offer', 'featured_popular'),
        }),
        ('Homepage Visibility', {
            'fields': (
                'featured_homepage_almirah',
                'featured_homepage_cooler',
                'featured_homepage_trunk',
                'featured_homepage_stand',
                'featured_homepage',
            ),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    actions = [export_as_csv]


@admin.register(SliderImage)
class SliderImageAdmin(SuperuserOnlyAdmin):
    list_display = ('caption', 'sort_order', 'active', 'image_preview')
    list_editable = ('sort_order', 'active')
    ordering = ('sort_order',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:80px; object-fit:cover;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(SerialNumberRecord)
class SerialNumberRecordAdmin(SuperuserOnlyAdmin):
    list_display = (
        'serial_number',
        'product',
        'customer_name',
        'technician_name',
        'product_checker_name',
        'purchase_date',
        'warranty_expiry',
        'warranty_valid',
    )
    list_filter = ('product', 'warranty_expiry')
    search_fields = ('serial_number', 'customer_name', 'customer_phone', 'technician_name', 'product_checker_name')
    readonly_fields = ('created_at',)
    actions = [export_as_csv]

    fieldsets = (
        ('Serial Record Details', {
            'fields': ('product', 'serial_number', 'customer_name', 'customer_phone', 'customer_address', 'purchase_date', 'warranty_expiry', 'technician_name', 'product_checker_name'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

    def warranty_valid(self, obj):
        return obj.warranty_valid

    warranty_valid.boolean = True
    warranty_valid.short_description = 'Warranty Active'


@admin.register(Complaint)
class ComplaintAdmin(ComplaintStaffAdmin):
    list_display = (
        'customer_name',
        'product_type',
        'serial_number',
        'phone',
        'technician_name',
        'status',
        'created_at',
        'bill_thumbnail',
    )
    list_editable = ('status',)
    list_filter = ('status', 'product_type')
    search_fields = ('phone', 'serial_number', 'customer_name')
    readonly_fields = ('created_at', 'updated_at', 'bill_thumbnail')
    actions = [export_as_csv]

    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'email', 'phone'),
        }),
        ('Product & Complaint', {
            'fields': ('product_type', 'serial_number', 'bill_copy', 'bill_thumbnail', 'message'),
        }),
        ('Support Track', {
            'fields': ('technician_name', 'status'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def bill_thumbnail(self, obj):
        if obj.bill_copy:
            return format_html(
                '<img src="{}" style="max-height:120px; object-fit:contain;" />',
                obj.bill_copy.url,
            )
        return '-'

    bill_thumbnail.short_description = 'Bill Copy Preview'


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(ComplaintStaffAdmin):
    list_display = (
        'name',
        'email',
        'phone',
        'subject',
        'resolved',
        'created_at',
    )
    list_editable = ('resolved',)
    list_filter = ('resolved', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject')
    readonly_fields = ('created_at',)
    actions = [export_as_csv]


@admin.register(Order)
class OrderAdmin(SuperuserOnlyAdmin):
    change_list_template = 'admin/store/order/change_list.html'
    list_display = (
        'order_number',
        'customer_name',
        'customer_phone',
        'payment_status',
        'delivery_status',
        'total_amount',
        'order_date',
    )
    list_editable = ('delivery_status',)
    list_filter = ('payment_status', 'delivery_status', 'order_date')
    search_fields = ('order_number', 'customer_name', 'customer_phone', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('created_at', 'updated_at', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'transaction_date')
    actions = [export_as_csv]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        extra_context['total_revenue'] = queryset.aggregate(total=models.Sum('total_amount'))['total'] or 0
        current_month = timezone.localdate().month
        current_year = timezone.localdate().year
        extra_context['monthly_revenue'] = queryset.filter(
            order_date__year=current_year,
            order_date__month=current_month,
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(HomepageBanner)
class HomepageBannerAdmin(SuperuserOnlyAdmin):
    list_display = ('title', 'active', 'sort_order', 'banner_preview')
    list_editable = ('active', 'sort_order')
    ordering = ('sort_order',)
    readonly_fields = ('banner_preview',)
    actions = [export_as_csv]

    def banner_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px; object-fit:cover;"/>', obj.image.url)
        return '-'

    banner_preview.short_description = 'Preview'


@admin.register(Review)
class ReviewAdmin(SuperuserOnlyAdmin):
    list_display = (
        'product',
        'reviewer_name',
        'product_type',
        'rating',
        'is_approved',
        'created_at',
    )
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'product_type')
    search_fields = ('reviewer_name', 'reviewer_email', 'product__name')
    actions = [export_as_csv]


admin.site.site_header = 'Sunil Trunk House Admin'
admin.site.index_title = 'Sunil Trunk House Dashboard'
admin.site.site_title = 'Sunil Trunk House'
