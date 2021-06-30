from django.db import models
from django.contrib.auth.models import User
from core.models import Item
from django.dispatch import receiver
from django.db.models.signals import post_save
from PIL import Image

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    email = models.EmailField(
        max_length=50, blank=True, null=True, unique=True)
    last_name = models.CharField(max_length=50)
    products = models.ManyToManyField(Item)
    phone_number = models.CharField(max_length=11)
    address = models.CharField(max_length=50)
    date_join = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    image = models.ImageField(upload_to='profile')

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
