from django.contrib import admin
from .models import Client, Category, Product, Review, Order, OrderItem, Profile


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'one_price', 'stock_quantity')
    list_editable = ('one_price', 'stock_quantity')
    list_filter = ('stock_quantity',)
    search_fields = ('product__name',)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'user')


class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('products', 'quantity', 'orders')
    list_filter = ('orders__clients',)


admin.site.register(Client, ClientAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem, OrderItemsAdmin)
admin.site.register(Profile)


# search laukas atjungtam profiliui isjungtas
# profilio redagavimas su visais laukais
# i krepseli pridejimas to paties produkto kelis kartus
# jei pavyks  checkouta sutvarkyti
