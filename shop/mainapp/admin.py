from django.contrib import admin
from . import models
from django import forms
from django.forms import ModelChoiceField, ModelForm
from PIL import Image
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
#from .models import *

# Register your models here.


class NotebookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe('<span style="color:red; font-size:14px;">Завантажуйте зображення з мінімальним розширенням {} x {}</span>'.format(*models.Product.MIN_RESOLUTION))

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_height, min_width = models.Product.MIN_RESOLUTION
        max_height, max_width = models.Product.MAX_RESOLUTION
        if image.size > models.Product.MAX_IMAGE_SIZE:
            raise ValidationError('Розмір картинки більший за 3MB')
        if img.height < min_height or img.width < min_width:
            raise ValidationError('Розширення картинки менше мінімального!')
        if img.height > min_height or img.widrh > min_width:
            raise ValidationError('Розширення картинки більше максимального!')

        return image



class SmartphoneAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(models.Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class NotebookAdmin(admin.ModelAdmin):

    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(models.Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(models.Category)
admin.site.register(models.Notebook, NotebookAdmin)
admin.site.register(models.Smartphone, SmartphoneAdmin)
admin.site.register(models.CartProduct)
admin.site.register(models.Cart)
admin.site.register(models.Customer)
