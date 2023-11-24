from django.contrib import admin
from .models import Script, Features, Category

# Register your models here.

admin.site.register(Features)


class ThemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title", )}


admin.site.register(Script, ThemeAdmin)

admin.site.register(Category)
