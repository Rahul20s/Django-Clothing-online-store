# orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # Improves performance for many products

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address',
                    'postal_code', 'city', 'paid', 'status', 'created', 'updated']
    list_filter = ['paid', 'status', 'created', 'updated']
    search_fields = ['id', 'first_name', 'last_name', 'email']
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped']

    def mark_as_paid(self, request, queryset):
        queryset.update(paid=True, status='processing')
    mark_as_paid.short_description = "Mark selected orders as paid and processing"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected orders as shipped"