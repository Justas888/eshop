from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Client(models.Model):
    """
    Atstovauja klientą su asmenine informacija.
    """
    first_name = models.CharField('Name', max_length=100)
    last_name = models.CharField('Surname', max_length=100)
    phone_number = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"{self.user} {self.user.email}"


class Category(models.Model):
    """
    Kategorija, apibūdinanti produktų grupę.
    """
    name = models.CharField('Name', max_length=255)
    description = models.TextField('Category description', max_length=2000, default='Category description etc.')
    foto = models.ImageField('Foto', upload_to='foto', null=True, blank=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Produktas su pavadinimu, aprašymu, kaina, kiekiu sandėlyje, kategorija, foto.
    """
    name = models.CharField('Name', max_length=255)
    description = models.TextField('Product description', max_length=2000, default='Product description etc.')
    one_price = models.FloatField()
    stock_quantity = models.IntegerField()
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    foto = models.ImageField('Foto', upload_to='foto', null=True, blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Užsakymas, turintis statusą, klientą ir sukūrimo datą.
    """
    STATUS_ORDER = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Shipped', 'Shipped'),
    ]
    status = models.CharField('Status',
                              max_length=10,
                              choices=STATUS_ORDER,
                              default='Pending',
                              blank=True,
                              help_text='Order is pending')
    clients = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.pk} - {self.clients}"


class OrderItem(models.Model):
    """
    Užsakymo prekių detalės, įskaitant prekę ir jos kiekį.
    """
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    orders = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.products.name} - {self.quantity} pcs"


class Review(models.Model):
    """
    Kliento atsiliepimas apie produktą, su vertinimu ir komentarais.
    """
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    clients = models.ForeignKey(Client, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_date = models.DateTimeField()

    def __str__(self):
        return f"Review by {self.clients} for {self.products.name}"


class Profile(models.Model):
    """
    Vartotojo profilis su nuotrauka, susijęs su Django vartotoju.
    """
    picture = models.ImageField(upload_to='profile_pics', blank=True, default='default_user.png')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture.path:
            img = Image.open(self.picture.path)
            thumb_size = (150, 150)
            img.thumbnail(thumb_size)
            img.save(self.picture.path)
