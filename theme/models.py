from django.db import models
from django.urls import reverse
import uuid
from django.utils.text import slugify

# Create your models here.


class Script(models.Model):
    title = models.TextField(max_length=500, null=True)
    image = models.ImageField(max_length=255, null=True, blank=True)
    preview_link = models.TextField(max_length=255, blank=True, null=True)
    details_link = models.TextField(max_length=500, blank=True, null=True)
    script_id = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=250, null=True)
    ratingCount = models.IntegerField(null=True, blank=True)
    salesCount = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    lastUpdate = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Script, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail', args=[self.slug])

    def __str__(self):
        return self.title


class Features(models.Model):
    text = models.TextField(max_length=255, blank=True)
    script = models.ForeignKey(
        Script, related_name="description", default="script", on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name
