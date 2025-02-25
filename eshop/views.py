from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from .models import Product, Category, User, Order, OrderItem
from .utils import check_password
from .forms import ProfileUpdateForm, UserUpdateForm, ClientUpdateForm


def main_page(request):
    """
    Pagrindinio puslapio rodymas.
    """
    return render(request, 'main_page.html')


@login_required
def products(request):
    """
    Rodomi visi produktai su puslapiavimu.
    Funkcija ištraukia visus produktus iš duomenų bazės, apdoroja juos
    puslapiavimui ir perduoda į šabloną, kad vartotojas galėtų matyti tik
    nustatytą dalį produktų vienu metu(8 vnt. per puslapį).
    """
    all_products = Product.objects.all()
    paginator = Paginator(all_products, 8)
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)

    context = {'products': paged_products}
    return render(request, 'products.html', context)


@login_required
def category_products(request, category_id):
    """
    Funkcija gauna produktus pagal kategorijos ID ir atvaizduoja juos
    kategorijos puslapyje.
    """
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(categories=category)
    return render(request, 'category_products.html', {'category': category, 'products': products})


@login_required
def categories(request):
    """
    Funkcija ištraukia visų kategorijų sąrašą ir perduoda į šabloną,
    kad vartotojas galėtų matyti visas kategorijas.
    """
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'categories.html', context)


@login_required
def product_detail(request, id):
    """
    Funkcija gauna konkretų produktą pagal jo ID ir atvaizduoja jo detales
    aprašytas šablone.
    """
    product = get_object_or_404(Product, id=id)
    context = {'product': product}
    return render(request, 'product_detail.html', context)


@login_required
def search(request):
    """
    Funkcija gauna vartotoja įvestą paieškos užklausą ir ieško produktų
    pagal pavadinimą.
    """
    query = request.GET.get('search_text')
    search_results = Product.objects.filter(
        Q(name__icontains=query))
    context = {'query': query, 'products': search_results}
    return render(request, 'products.html', context)


@csrf_protect
def register_user(request):
    """
    Funkcija apdoroja vartotojo registracijos formą. Ji tikrina, ar įvestas
    slaptažodis atitinka reikalavimus, ar slaptažodžiai sutampa ir ar
    vartotojo vardas, bei el. paštas jau nėra užimti. Jei rezultatas teigiamas,
    sukuria naują vartotoją.
    """
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
    """
    Funkcija leidžia vartotojui atnaujinti savo profilį( el.paštą, tel. nr.,
    adresą ir profilinę nuotrauką). Jei paspaudžiamas mygtukas, forma išsaugoma
    ir pateikiama atitinkama žinutė.
    """
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        c_form = ClientUpdateForm(request.POST, request.FILES, instance=request.user.client)
        if p_form.is_valid() and u_form.is_valid() and c_form.is_valid():
            p_form.save()
            u_form.save()
            c_form.save()
            messages.info(request, "Profile updated")
        else:
            messages.error(request, "Profile has no changes")
        return redirect('profile')

    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
        u_form = UserUpdateForm(instance=request.user)
        c_form = ClientUpdateForm(instance=request.user.client)

    context = {
        'p_form': p_form,
        'u_form': u_form,
        'c_form': c_form,
    }

    return render(request, 'profile.html', context=context)


@login_required
def add_to_cart(request, product_id):
    """
    Funkcija leidžia vartotojui pridėti prekę į krepšelį. Jei prekė jau yra,
    jos kiekis padidėja. Jei prekės nėra, ji pridedama su 1 vnt. Taip pat
    jei saugomas prekių kiekis nepakankamas gauname pranešimą.
    """
    cart = request.session.get('cart', {})
    product = Product.objects.get(id=product_id)

    if product.stock_quantity <= 0:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return redirect('products')

    if str(product_id) in cart:
        if cart[str(product_id)]['quantity'] < product.stock_quantity:
            cart[str(product_id)]['quantity'] += 1
            messages.success(request, f"Added another {product.name} to your cart.")
        else:
            messages.error(request, f"Sorry, you can't add more of {product.name}. "
                                    f"Only {product.stock_quantity} is available.")
    else:
        if product.stock_quantity > 0:
            cart[str(product_id)] = {
                'name': product.name,
                'price': product.one_price,
                'quantity': 1,
                'image': product.foto.url if product.foto else None
            }
            messages.success(request, f"Added {product.name} to your cart.")
        else:
            messages.error(request, f"Sorry, {product.name} is out of stock.")
    request.session['cart'] = cart
    return redirect('products')


@login_required
def remove_from_cart(request, product_id):
    """
    Funkcija leidžia vartotojui pašalinti prekę iš krepšelio pagal prekei
    skirtą ID. Jei prekė randama krepšelyje, ji bus pašalinama ir krepšelis
    atnaujinamas.
    """
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, "Product has been removed from cart.")
    else:
        messages.error(request, "Cannot find product in the cart.")
    return redirect('cart')


@login_required
def view_cart(request):
    """
    Funkcija leidžia vartotojui peržiūrėti prekes, esančias jo krepšelyje
    ir rodyti bendrą krepšelio vertę (visų prekių kainų suma pagal kiekį).
    """
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})


@login_required
def checkout(request):
    """
    Funkcija apdoroja užsakymą ir apmokėjimo procesą(dalinai). Jei krepšelis
    yra tuščias, vartotojui pateikiama klaidos žinutė. Jei užsakymas dar nėra
    sukurtas, sukuriamas naujas užsakymas su "Pending" būsena. Po sėkmingo
    užsakymo sukūrimo ištrinamas krepšelis iš sesijos ir išsiunčiama
    patvirtinimo žinutė el. paštu.
    """
    client = request.user.client
    order = Order.objects.filter(clients=client, status='Pending').first()
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty. Please add items to your cart before proceeding to checkout.")
        return redirect('cart')

    if not order:
        order = Order.objects.create(
            clients=client,
            status='Pending'
        )
    order_items = OrderItem.objects.filter(orders=order)
    order_items.delete()

    for item in cart.values():
        product = Product.objects.get(name=item['name'])
        OrderItem.objects.create(
            orders=order,
            products=product,
            quantity=item['quantity']
        )

    send_mail(
        'Your Order Confirmation',
        f'Thank you for your order: The payment instructions are HERE.',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False,
    )
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('order_success')


@login_required
def order_success(request):
    """
    Funkcija atvaizduoja užsakymo sėkmės pusalpį, kai užsakymas yra užbaigtas
    """
    return render(request, 'order_success.html')
