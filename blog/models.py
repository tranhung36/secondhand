from django.db import models
from tinymce import HTMLField
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify

User = get_user_model()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    slug = models.SlugField(blank=True, null=True, unique=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        super().save(*args, **kwargs)


class Post(models.Model):
    slug = models.SlugField(blank=True, null=True, unique=True)
    title = models.CharField(max_length=200)
    content = HTMLField('Content')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    comment_count = models.IntegerField(default=0)
    category = models.ManyToManyField(Category)
    thumbnail = models.ImageField()
    featured = models.BooleanField(default=False)
    overview = models.TextField()
    view_count = models.IntegerField(default=0)
    previous_post = models.ForeignKey('self', related_name='previous_post', on_delete=models.SET_NULL, blank=True, null=True)
    next_post = models.ForeignKey('self', related_name='next_post', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post", kwargs={"slug": self.slug})
