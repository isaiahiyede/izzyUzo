from django.contrib import admin
from models import *
# Register your models here.

class ShoppingCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'desc', 'created_by')

admin.site.register(ShoppingCategory, ShoppingCategoryAdmin)

class ShoppingOrderAdmin(admin.ModelAdmin):
	list_display = ('user', 'tracking_number', 'quantity', 'shipping_cost')

admin.site.register(ShoppingOrder, ShoppingOrderAdmin)

class ShoppingItemAdmin(admin.ModelAdmin):
	list_display = ('created_by', 'name', 'desc', 'weight', 'shoppingItem_image', 'price', 'category', 'shopping_order')

admin.site.register(ShoppingItem, ShoppingItemAdmin)
admin.site.register(Category)
admin.site.register(SubCategory)

class AddInventoryAdmin(admin.ModelAdmin):
	list_display = ('title','description', 'item_image', 'price', 'sold', )
admin.site.register(AddInventory, AddInventoryAdmin)

# class CartAdmin(admin.ModelAdmin):
# 	list_display = ('description', 'docfile', 'price', 'quantity', 'details', 'ordered', 'order', 'total', 'client', 'created_on',)
admin.site.register(Cart)

class UserOrderAdmin(admin.ModelAdmin):
	list_display = ('order_number',)
admin.site.register(UserOrder, UserOrderAdmin)