from django.contrib import admin
from .models import Product, Customer, Supplier, Expense, Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    readonly_fields = ('get_subtotal',)  # must match method name in model
    extra = 0


class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleItemInline]
    list_display = ("id", "date", "user", "total_amount")
    readonly_fields = ("date",)


admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Supplier)
admin.site.register(Expense)
admin.site.register(Sale, SaleAdmin)
# Do NOT register SaleItem separately if using inline
# admin.site.register(SaleItem)
