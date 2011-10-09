from shop.models import *
from django.contrib import admin

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
   
class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'is_paid', 'owner', 'notes')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'email', 'is_published')
    
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'parent')


class UniqueProductAdmin(admin.ModelAdmin):
    list_display = ('parent_product', 'weight', 'price', 'is_sale_price', 'is_active')
    
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Address)
admin.site.register(Shopper)
admin.site.register(UniqueProduct, UniqueProductAdmin)
admin.site.register(Basket)
admin.site.register(Order, OrderAdmin)
admin.site.register(Discount)
admin.site.register(Photo)
admin.site.register(Referee)
admin.site.register(WeLike)
admin.site.register(Notify)
admin.site.register(Page, PageAdmin)
admin.site.register(Review, ReviewAdmin)



