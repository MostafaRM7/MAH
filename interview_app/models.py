from django.db import models
from django.utils import timezone

from admin_app.models import PricePack
from question_app.models import Questionnaire
from user_app.models import Profile, District


def get_current_date():
    return timezone.now().date()


# Create your models here.

class Interview(Questionnaire):
    APPROVED_ADMIN = 'aa'
    PENDING_ADMIN = 'pa'
    REJECTED_ADMIN = 'ra'
    APPROVED_EMPLOYER = 'ae'
    PENDING_EMPLOYER = 'pe'
    REJECTED_EMPLOYER = 're'
    APPROVAL_STATUS = (
        (APPROVED_ADMIN, 'تایید شده توسط ادمین'),
        (PENDING_ADMIN, 'در انتظار تایید ادمین'),
        (REJECTED_ADMIN, 'رد شده توسط ادمین'),
        (APPROVED_EMPLOYER, 'تایید شده توسط کارفرما'),
        (PENDING_EMPLOYER, 'در انتظار تایید کارفرما'),
        (REJECTED_EMPLOYER, 'رد شده توسط کارفرما')
    )
    interviewers = models.ManyToManyField(Profile, related_name='interviews', verbose_name='مصاحبه کنندگان', blank=True)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default=PENDING_ADMIN,
                                       verbose_name='وضعیت تایید')
    add_to_approve_queue = models.BooleanField(default=False, verbose_name='به صف تایید اضافه شود')
    districts = models.ManyToManyField(District, related_name='interviews', verbose_name='مناطق')
    goal_start_date = models.DateField(default=get_current_date, verbose_name='تاریخ شروع هدف')
    goal_end_date = models.DateField(default=get_current_date, verbose_name='تاریخ پایان هدف')
    answer_count_goal = models.PositiveIntegerField(verbose_name='تعداد پاسخ هدف')
    price_pack = models.ForeignKey(PricePack, on_delete=models.CASCADE, verbose_name='بسته قیمت')

    def __str__(self):
        return self.name


class Ticket(models.Model):
    text = models.TextField(verbose_name='متن')
    source = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_tickets', verbose_name='فرستنده')
    destination = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_tickets')
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, null=True, blank=True, related_name='tickets',
                                  verbose_name='پروژه پرسشگری')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
