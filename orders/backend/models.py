from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    surname = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ["surname", "name"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.surname} {self.name}"


class Shop(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(null=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    shops = models.ManyToManyField(
        Shop,
        related_name="categories"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="info"
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="info"
    )

    class Meta:
        verbose_name = "Product info"
        verbose_name_plural = "Products info"


class Parameter(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name = "Parameter"
        verbose_name_plural = "Parameters"

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    value = models.CharField(max_length=100)
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name="product_parameters"
    )
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name="product_parameters"
    )

    class Meta:
        verbose_name = "Product parameter"
        verbose_name_plural = "Product parameters"


class Order(models.Model):

    class Status(models.TextChoices):
        CREATED = "CR", "Created"
        ASSEMBLED = "AD", "Assembled"
        SENT = "ST", "Sent"
        DELIVERED = "DD", "Delivered"
        CANCELED = "CD", "Canceled"

    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=Status.choices)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-dt"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.dt


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="items"
    )

    class Meta:
        verbose_name = "Order item"
        verbose_name_plural = "Order items"


class Contact(models.Model):
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=80)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=10)
    building = models.CharField(max_length=5)
    structure = models.CharField(max_length=5)
    apartment = models.CharField(max_length=10)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contacts",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        return f"{self.city} {self.street}"
