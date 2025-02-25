from django.contrib import admin
from .models import Client, Category, Product, Review, Order, OrderItem, Profile


class ProductAdmin(admin.ModelAdmin):
    """
    Django administratoriaus sąsajos konfigūracija produktams:
    rodoma produkto ID, pavadinimas, kaina ir sandėlio kiekis,
    galimybė redaguoti kainą ir kiekį, filtruoti pagal sandėlio kiekį
    ir ieškoti pagal produkto pavadinimą.
    """
    list_display = ('id', 'name', 'one_price', 'stock_quantity')
    list_editable = ('one_price', 'stock_quantity')
    list_filter = ('stock_quantity',)
    search_fields = ('product__name',)


class ClientAdmin(admin.ModelAdmin):
    """
    Django administratoriaus sąsajos konfigūracija klientams:
    rodoma kliento vardas, pavardė ir susijęs vartotojas.
    """
    list_display = ('first_name', 'last_name', 'user')


class OrderItemsAdmin(admin.ModelAdmin):
    """
    Django administratoriaus sąsajos konfigūracija užsakymo prekėms:
    rodoma prekė, jos kiekis ir susijęs užsakymas, galimybė filtruoti
    pagal užsakymo kliento informaciją.
    """
    list_display = ('products', 'quantity', 'orders')
    list_filter = ('orders__clients',)


admin.site.register(Client, ClientAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem, OrderItemsAdmin)
admin.site.register(Profile)
