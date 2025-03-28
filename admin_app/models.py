from django.db import models

# Create your models here.


class PricePack(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='اسم', error_messages={
        'required': 'لطفا اسم را وارد کنید',
        'max_length': 'اسم باید کمتر از 255 کاراکتر باشد'
    })
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    price = models.PositiveIntegerField(verbose_name='قیمت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        return f'{self.name} - {self.price}'
