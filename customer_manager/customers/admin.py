from django.contrib import admin
from .models import Customer
from .models import Product
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]

admin.site.register(Product)
admin.site.register(Customer)