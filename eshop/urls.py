from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='home'),
    path('products/', views.products, name='products'),
    path('categories/', views.categories, name='categories'),
    path('register/', views.register_user, name='register'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('profile/', views.get_user_profile, name='profile'),
    path('search/', views.search, name='search'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('cart/', views.view_cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
]