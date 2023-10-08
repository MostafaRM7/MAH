from django.db import models

from question_app.models import Questionnaire
from user_app.models import Profile, District


# Create your models here.

class Interview(Questionnaire):
    APPROVED = 'a'
    PENDING = 'p'
    REJECTED = 'r'
    APPROVAL_STATUS = (
        (APPROVED, 'تایید شده'),
        (PENDING, 'در انتظار تایید'),
        (REJECTED, 'رد شده')
    )
    pay_per_answer = models.FloatField(verbose_name='پرداختی برای هر پاسخ')
    interviewers = models.ManyToManyField(Profile, related_name='interviews', verbose_name='مصاحبه کنندگان')
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default=PENDING,
                                       verbose_name='وضعیت تایید')
    add_to_approve_queue = models.BooleanField(default=False, verbose_name='به صف تایید اضافه شود')
    districts = models.ManyToManyField(District, related_name='interviews', verbose_name='مناطق')
    goal = models.TextField(verbose_name='هدف', null=True, blank=True)
    answer_count_goal = models.PositiveIntegerField(verbose_name='تعداد پاسخ هدف')

    def __str__(self):
        return self.name

    @property
    def total_pay(self):
        return self.pay_per_answer * self.answer_count_goal


class Ticket(models.Model):
    text = models.TextField(verbose_name='متن')
    source = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tickets', verbose_name='فرستنده')
    destination = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_tickets')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')