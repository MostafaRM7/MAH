from random import randint

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    ROLE_CHOICES = (
        ('i', 'پرسشگر'),
        ('e', 'کارفرما'),
        ('ie', 'پرسشگر و کارفرما'),
        ('n', 'بدون نقش'),
    )
    phone_number = models.CharField(max_length=20, validators=[
        RegexValidator(regex='^09[0-9]{9}$', message='شماره تلفن همراه وارد شده صحیح نمی باشد')], unique=True,
                                    verbose_name='شماره تلفن همراه')
    username = None
    USERNAME_FIELD = 'phone_number'
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, verbose_name='نقش', default='n')

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.phone_number


class OTPToken(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='otp_token',
                                verbose_name='کاربر')
    token = models.CharField(max_length=6, null=True, blank=True,
                             verbose_name='کد فعال سازی', editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    try_count = models.PositiveIntegerField(default=0, verbose_name='تعداد تلاش ها')


    def __str__(self):
        return f'{self.user} - {self.token}'


class Profile(User):
    GENDER_CHOICES = (
        ('m', 'مرد'),
        ('f', 'زن'),
    )
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='جنسیت', null=True, blank=True)
    address = models.TextField(verbose_name='آدرس', null=True, blank=True)
    birth_date = models.DateField(verbose_name='تاریخ تولد', null=True, blank=True)
    nationality = models.ForeignKey('Country', on_delete=models.CASCADE, verbose_name='ملیت', null=True, blank=True)
    province = models.ForeignKey('Province', on_delete=models.CASCADE, verbose_name='استان', null=True, blank=True)
    preferred_districts = models.ManyToManyField('District', verbose_name='مناطق مورد علاقه', blank=True)
    avatar = models.ImageField(upload_to='avatars/', verbose_name='تصویر پروفایل', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='زمان آخرین بروزرسانی')
    ask_for_interview_role = models.BooleanField(default=False, verbose_name='درخواست نقش پرسشگر')
    is_interview_role_accepted = models.BooleanField(verbose_name='درخواست پرسشگری تایید شده/نشده', null=True,
                                                     blank=True)


class Country(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام کشور', unique=True)

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام استان', unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='کشور', related_name='provinces')

    def __str__(self):
        return f'{self.name} - {self.country}'


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام شهر', unique=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name='استان', related_name='cities')

    def __str__(self):
        return f'{self.name} - {self.province}'


class District(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام منطقه')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='شهر', related_name='districts')

    def __str__(self):
        return f'{self.name} - {self.city}'


class UserRoleApproveQueue(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_role_approve_queue',
                             verbose_name='کاربر')
    role = models.CharField(max_length=2, choices=User.ROLE_CHOICES, verbose_name='نقش')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان تایید')
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده')

    def __str__(self):
        return f'{self.user} - {self.role} - {self.created_at} - {self.is_approved}'


class Resume(models.Model):
    owner = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='پروفایل', related_name='resume')
    linkedin = models.CharField(verbose_name='لینکدین', max_length=255, null=True, blank=True)
    file = models.FileField(upload_to='resume', verbose_name='فایل رزومه', null=True, blank=True)

    def __str__(self):
        return f'{self.owner} - {self.file}'


class WorkBackground(models.Model):
    company = models.CharField(max_length=50, verbose_name='نام شرکت')
    position = models.CharField(max_length=50, verbose_name='عنوان شغلی')
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    description = models.TextField(verbose_name='توضیحات')
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, verbose_name='رزومه',
                               related_name='work_backgrounds')

    def __str__(self):
        return f'{self.resume} - {self.company} - {self.position}'


class EducationalBackground(models.Model):
    DEGREE_CHOICES = (
        ('d', 'دیپلم'),
        ('b', 'کارشناسی'),
        ('m', 'کارشناسی ارشد'),
        ('p', 'دکتری'),
    )
    EDU_TYPE_CHOICES = (
        ('u', 'دانشگاهی'),
        ('h', 'حوزوی'),
        ('o', 'سایر'),
    )
    degree = models.CharField(max_length=2, choices=DEGREE_CHOICES, verbose_name='مدرک')
    edu_type = models.CharField(max_length=2, choices=EDU_TYPE_CHOICES, default='u', verbose_name='نوع مدرک')
    field = models.CharField(max_length=255, verbose_name='رشته')
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, verbose_name='رزومه',
                               related_name='educational_backgrounds')
    university = models.CharField(max_length=255, verbose_name='مرکز آموزشی')

    def __str__(self):
        return f'{self.resume} - {self.field}'


class Skill(models.Model):
    LEVEL_CHOICES = (
        (1, 'مبتدی'),
        (2, 'متوسط'),
        (3, 'حرفه ای'),
        (4, 'خبره'),
        (5, 'مسلط')
    )
    field = models.CharField(max_length=255, verbose_name='زمینه مهارت')
    level = models.PositiveIntegerField(verbose_name='سطح مهارت', choices=LEVEL_CHOICES)
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, verbose_name='رزومه', related_name='skills')

    def __str__(self):
        return f'{self.resume} - {self.field}'


class Achievement(models.Model):
    field = models.CharField(max_length=255, verbose_name='زمینه')
    institute = models.CharField(max_length=255, verbose_name='مرکز')
    year = models.DateField(verbose_name='سال')
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, verbose_name='رزومه', related_name='achievements')

    def __str__(self):
        return f'{self.resume} - {self.field}'


class ResearchHistory(models.Model):
    link = models.URLField(verbose_name='لینک')
    year = models.DateField(verbose_name='سال')
    field = models.CharField(max_length=255, verbose_name='زمینه')
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, verbose_name='رزومه',
                               related_name='research_histories')

    def __str__(self):
        return f'{self.resume} - {self.field}'
