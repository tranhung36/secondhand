from django.conf import settings
from django.shortcuts import reverse
from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from django.utils.text import slugify
from PIL import Image


# List categories item
CATEGORY_CHOICES = (
    ('C', 'Clothes'),
    ('S', 'Shoes'),
    ('A', 'Accessories'),
    ('W', 'Watches')
)
# List label item (new, used)
LABEL_CHOICES = (
    ('N', 'New'),
    ('U', 'Used')
)


class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category, related_name='subcategory', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'sub categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super(SubCategory, self).save(*args, **kwargs)


class Item(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES,
                             max_length=1, blank=True, null=True)
    description = models.TextField()
    size = models.IntegerField(default=42)
    quantity = models.IntegerField(default=1)
    condition_number = models.PositiveIntegerField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})

    def get_display_price(self):
        return self.price


class Images(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return self.item.title

    def save(self, *args, **kwargs):
        super(Images, self).save(*args, **kwargs)  # saving image first

        img = Image.open(self.image.path)  # Open image using self

        if img.height > 774 or img.width > 808:
            new_img = (774, 808)
            img.thumbnail(new_img)
            img.save(self.image.path)  # saving image at the same path


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=15)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_subtotal(self):
        subtotal = 0
        for order_item in self.items.all():
            if order_item.item.discount_price:
                subtotal += order_item.get_total_discount_item_price()
            else:
                subtotal += order_item.get_total_item_price()
        return subtotal

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon and total > self.coupon.amount:
            total -= self.coupon.amount
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12)
    street_address = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    amount = models.FloatField()
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f'{self.pk}'
