from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from unicodedata import category

from .models import Client, Product, Category, User, Order, OrderItem
from .utils import check_password
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserUpdateForm
from django.views import generic
from django.http import HttpResponse


def main_page(request):
    return render(request, 'main_page.html')


@login_required
def products(request):
    all_products = Product.objects.all()
    paginator = Paginator(all_products, 8)
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)

    context = {'products': paged_products}
    return render(request, 'products.html', context)


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(categories=category)  # Filtruoti pagal kategoriją
    return render(request, 'category_products.html', {'category': category, 'products': products})


@login_required
def categories(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'categories.html', context)


@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    context = {'product': product}
    return render(request, 'product_detail.html', context)


@login_required
def search(request):
    query = request.GET.get('search_text')
    search_results = Product.objects.filter(
        Q(name__icontains=query))
    context = {'query': query, 'products': search_results}
    return render(request, 'products.html', context)


@csrf_protect
def register_user(request):
    if request.method == 'GET':
        return render(request, 'registration/registration.html')

    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not check_password(password):
            messages.error(request, 'Password needs minimum 8 symbols!!!')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username {username} is already taken')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, f'Email {email} is already taken')
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.info(request, f'User {username} successfuly registered!')
        return redirect('login')


@login_required
def get_user_profile(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            p_form.save()
            u_form.save()
            messages.info(request, "Profile updated")
        else:
            messages.error(request, "Profile has no changes")
        return redirect('profile')

    p_form = ProfileUpdateForm(instance=request.user.profile)
    u_form = UserUpdateForm(instance=request.user)

    context = {
        'p_form': p_form,
        'u_form': u_form
    }

    return render(request, 'profile.html', context=context)


@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    quantity = request.POST.get('quantity', 1)

    cart = request.session.get('cart', {})
    if product_id in cart:
        cart[product_id]['quantity'] += int(quantity)
    else:
        cart[product_id] = {
            'name': product.name,
            'price': product.one_price,
            'quantity': int(quantity),
            'image': product.foto.url if product.foto else None
        }

    request.session['cart'] = cart
    messages.success(request, f"Product {product.name} has been added to the cart!")
    return redirect('products')  # Nukreipia atgal į prekių puslapį


@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Product is removed from your cart.")
    return redirect('cart')  # Nukreipia į krepšelio puslapį


# Krepšelio puslapis
def view_cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

@login_required
def checkout(request):
    order = Order.objects.filter(clients=request.user.client, status='Pending').first()

    if order:
        order_items = OrderItem.objects.filter(order=order)
        order_items.delete()
        order.status = 'Completed'
        order.save()

        send_mail(
            'Your Order Confirmation',
            'Thank you for your order! The payment instructions have been sent to your email.',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        messages.info(request, "Your order has been placed successfully and payment instructions have been sent to your email.")
        return redirect('order_success')
    else:
        messages.error(request, "No active order found.")
        return redirect('cart')


def order_success(request):
    return render(request, 'order_success.html')