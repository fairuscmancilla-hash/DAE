from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class SiteSetting(models.Model):
    """Singleton with the portal content that editors manage from the admin."""

    site_name = models.CharField(max_length=100, default="Portal de Noticias")
    tagline = models.CharField(max_length=200, blank=True)
    announcement = models.CharField(
        max_length=200,
        blank=True,
        help_text="Banner shown on every page. Leave it empty to hide it.",
    )

    class Meta:
        verbose_name = "site setting"
        verbose_name_plural = "site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        type(self).objects.exclude(pk=1).delete()

    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:category_list", args=[self.slug])

    def __str__(self):
        return self.name


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author_profile")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="authors/", blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["user__first_name", "user__last_name"]
        verbose_name = "author"
        verbose_name_plural = "authors"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def __str__(self):
        return self.full_name


class Article(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    summary = models.CharField(max_length=300, help_text="Short lead shown on the cards.")
    body = models.TextField()
    featured_image = models.ImageField(upload_to="articles/", blank=True)
    published_at = models.DateTimeField()
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="articles")
    categories = models.ManyToManyField(Category, related_name="articles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "article"
        verbose_name_plural = "articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:article_detail", args=[self.slug])

    def __str__(self):
        return self.title
