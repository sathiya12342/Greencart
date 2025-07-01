from django.contrib import admin
from .models import *
from .models import Order
# Register your models here.

'''class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description')'''

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'status', 'ordered_date']
    list_filter = ['status']
    list_editable = ['status']
   
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)

