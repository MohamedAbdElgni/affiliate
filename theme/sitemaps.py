from django.contrib.sitemaps import Sitemap
from .models import Script


class ThemeSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Script.objects.all().order_by('-id')
