from django.db import models
from django.utils import timezone

from admin_app.models import PricePack
from question_app.models import Questionnaire
from user_app.models import Profile, District


def get_current_date():
    return timezone.now().date()


# Create your models here.

class Interview(Questionnaire):
    # 0
    PENDING_CONTENT_ADMIN = 'pending_content_admin'
    REJECTED_CONTENT_ADMIN = 'rejected_content_admin'
    # 1
    PENDING_LEVEL_ADMIN = 'pending_level_admin'
    # 2
    PENDING_PRICE_ADMIN = 'pending_price_admin'
    # 3
    PENDING_PRICE_EMPLOYER = 'pending_price_employer'
    # 4
    REJECTED_PRICE_EMPLOYER = 'rejected_price_employer'
    # 5
    SEARCHING_FOR_INTERVIEWERS = 'searching_for_interviewers'
    APPROVAL_STATUS = (
        (PENDING_CONTENT_ADMIN, 'در انتظار تایید محتوا توسط ادمین'),
        (PENDING_LEVEL_ADMIN, 'در انتظار تعیین سطح ادمین'),
        (PENDING_PRICE_ADMIN, 'در انتظار تعیین قیمت ادمین'),
        (REJECTED_CONTENT_ADMIN, 'رد محتوا شده توسط ادمین'),
        (PENDING_PRICE_EMPLOYER, 'در انتظار تایید قیمت توسط کارفرما'),
        (REJECTED_PRICE_EMPLOYER, 'رد قیمت شده توسط کارفرما'),
        (SEARCHING_FOR_INTERVIEWERS, 'در جست و جوی پرسشگر')
    )
    interviewers = models.ManyToManyField(Profile, related_name='interviews', verbose_name='مصاحبه کنندگان', blank=True)
    approval_status = models.CharField(max_length=255, choices=APPROVAL_STATUS, default=PENDING_CONTENT_ADMIN,
                                       verbose_name='وضعیت تایید')
    districts = models.ManyToManyField(District, related_name='interviews', verbose_name='مناطق')
    goal_start_date = models.DateField(default=get_current_date, verbose_name='تاریخ شروع هدف', null=True, blank=True)
    goal_end_date = models.DateField(default=get_current_date, verbose_name='تاریخ پایان هدف', null=True, blank=True)
    answer_count_goal = models.PositiveIntegerField(verbose_name='تعداد پاسخ هدف', null=True, blank=True)
    price_pack = models.ForeignKey(PricePack, on_delete=models.CASCADE, verbose_name='بسته قیمت', null=True, blank=True)
    required_interviewer_count = models.PositiveIntegerField(null=True, blank=True, verbose_name='تعداد پرسشگر مورد نیاز')

    def __str__(self):
        return self.name


class Ticket(models.Model):
    text = models.TextField(verbose_name='متن')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_tickets', verbose_name='فرستنده')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_tickets', verbose_name='دریافت کننده', null=True, blank=True)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, null=True, blank=True, related_name='tickets',
                                  verbose_name='پروژه پرسشگری')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
