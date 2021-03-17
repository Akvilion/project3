from django.contrib import admin
from . import models
from django import forms

# Register your models here.


class NotebookCategoryChoiceField(forms.ModelChoiceField):
    pass


class NotebookAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return NotebookCategoryChoiceField(models.Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(models.Category)
admin.site.register(models.Notebook, NotebookAdmin)
admin.site.register(models.Smartphone)
admin.site.register(models.CartProduct)
admin.site.register(models.Cart)
admin.site.register(models.Customer)
