from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.urls import reverse
# Create your models here.


User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Категорії')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (2000, 2000)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категорія', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Назва')
    slug = models.SlugField(unique=True)
    image = models.ImageField()
    description = models.TextField(verbose_name='Опис', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Ціна')

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     # image = self.image
    #     # img = Image.open(image)
    #     # min_height, min_width = self.MIN_RESOLUTION
    #     # max_height, max_width = self.MAX_RESOLUTION
    #     # if img.height < min_height or img.width < min_width:
    #     #     raise MinResolutionErrorException('Розширення картинки менше мінімального!')
    #     # if img.height > min_height or img.widrh > min_width:
    #     #     raise MaxResolutionErrorException('Розширення картинки більше максимального!')
    #     image = self.image
    #     img = Image.open(image)
    #     new_img = img.convert('RGB')
    #     resized_new_img = new_img.resize((600, 600), Image.ANTIALIAS)
    #     filestream = BytesIO()
    #     resized_new_img.save(filestream, 'JPEG', quality=90)
    #     resized_new_img.seek(0)
    #     name = '{}.{}'.format(*self.image.name.split('.'))
    #     self.image = InMemoryUploadedFile(filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None)
    #     super().save(*args, **kwargs)


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупець', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Кошик', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Загальна ціна')

    def __str__(self):
        return f'Продукт: {self.product.title} (для корзини)'


class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Власник', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Загальна ціна')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Користувач', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефону')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return f'Покупець {self.user.first_name} {self.user.last_name}'


class Notebook(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Діагональ')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor_freq = models.CharField(max_length=255, verbose_name='Частота проццесора')
    ram = models.CharField(max_length=255, verbose_name='Оперативна пам\'ять')
    video = models.CharField(max_length=255, verbose_name='Відеокарта')
    time_without_charge = models.CharField(max_length=255, verbose_name='Час роботи від акумулятора')

    def __str__(self):
        return f'{self.category.name} {self.title}'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Smartphone(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Діагональ')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплею')
    resolution = models.CharField(max_length=255, verbose_name='Розширення екрану')
    accum_volume = models.CharField(max_length=255, verbose_name='Об\'єм батареї')
    ram = models.CharField(max_length=255, verbose_name='оперативна пам\'ять')
    sd = models.BooleanField(default=True, verbose_name='Наявність SD карти')
    sd_volume_max = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Максимальний об\'єм оперативної пам\'яті'
    )
    main_cam_mp = models.CharField(max_length=255, verbose_name='Головна камера')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальна камера')

    def __str__(self):
        return f'{self.category.name} {self.title}'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class  LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(self, *args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True)
        return products


class LatestProducts:

    objects = LatestProductsManager()
