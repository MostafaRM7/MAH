from django.db import models

# Create your models here.


class PricePack(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='اسم')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='قیمت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        return f'{self.name} - {self.price}'
