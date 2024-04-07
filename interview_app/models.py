from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from admin_app.models import PricePack
from question_app.models import Questionnaire
from user_app.models import Profile
from user_app.models import District


def get_current_date():
    return timezone.now().date()


class PrivateInterviewer(models.Model):
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex='^09[0-9]{9}$', message='شماره تلفن همراه وارد شده صحیح نمی باشد')],
        unique=True,
        verbose_name='شماره تلفن همراه'
    )
    interview_code = models.CharField(max_length=20, verbose_name='کد پرسشگری')
    first_name = models.CharField(max_length=30, verbose_name='نام')
    last_name = models.CharField(max_length=30, verbose_name='نام خانوادگی')

    def __str__(self):
        return self.phone_number


class Interview(Questionnaire):
    PENDING_CONTENT_ADMIN = 'pending_content_admin'
    REJECTED_CONTENT_ADMIN = 'rejected_content_admin'
    PENDING_LEVEL_ADMIN = 'pending_level_admin'
    PENDING_PRICE_ADMIN = 'pending_price_admin'
    PENDING_PRICE_EMPLOYER = 'pending_price_employer'
    REJECTED_PRICE_EMPLOYER = 'rejected_price_employer'
    SEARCHING_FOR_INTERVIEWERS = 'searching_for_interviewers'
    REACHED_INTERVIEWER_COUNT = 'reached_interviewer_count'
    REACHED_ANSWER_COUNT = 'reached_answer_count'
    APPROVED_BY_ADMIN = 'approved_by_admin'
    APPROVAL_STATUS = (
        (PENDING_CONTENT_ADMIN, 'در انتظار تایید محتوا توسط ادمین'),
        (PENDING_LEVEL_ADMIN, 'در انتظار تعیین سطح ادمین'),
        (PENDING_PRICE_ADMIN, 'در انتظار تعیین قیمت ادمین'),
        (REJECTED_CONTENT_ADMIN, 'رد محتوا شده توسط ادمین'),
        (PENDING_PRICE_EMPLOYER, 'در انتظار تایید قیمت توسط کارفرما'),
        (REJECTED_PRICE_EMPLOYER, 'رد قیمت شده توسط کارفرما'),
        (SEARCHING_FOR_INTERVIEWERS, 'در جست و جوی پرسشگر'),
        (REACHED_INTERVIEWER_COUNT, 'دارای پرسشگر مورد نیاز'),
        (REACHED_ANSWER_COUNT, 'دارای تعداد پاسخ مورد نیاز'),
        (APPROVED_BY_ADMIN, 'تایید شده توسط ادمین'),
        # todo   از اقای کوتی بپرسم که در کدام بخش وقتی ادمین تایید میکنه محتوا منتشر میشه
    )
    interviewers = models.ManyToManyField(Profile, related_name='interviews', verbose_name='مصاحبه کنندگان', blank=True,
                                          null=True)
    privet_interviewers = models.ManyToManyField(PrivateInterviewer, related_name='privet_interviews',
                                                 verbose_name='مصاحبه کنندگان خصوصی', blank=True,
                                                 null=True)
    approval_status = models.CharField(max_length=255, choices=APPROVAL_STATUS, default=PENDING_CONTENT_ADMIN,
                                       verbose_name='وضعیت تایید')
    districts = models.ManyToManyField(District, related_name='interviews', verbose_name='مناطق', null=True, blank=True)
    goal_start_date = models.DateField(default=get_current_date, verbose_name='تاریخ شروع هدف', null=True, blank=True)
    goal_end_date = models.DateField(default=get_current_date, verbose_name='تاریخ پایان هدف', null=True, blank=True)
    answer_count_goal = models.PositiveIntegerField(verbose_name='تعداد پاسخ هدف', null=True, blank=True)
    required_interviewer_count = models.PositiveIntegerField(null=True, blank=True,
                                                             verbose_name='تعداد پرسشگر مورد نیاز')
    protocol = models.FileField(upload_to='media/', verbose_name='پروتکل ', null=True, blank=True)
    # , validators = [
    #     FileExtensionValidator(['.pdf', '.doc', '.docx', '.jpg', '.png'])]
    is_privet = models.BooleanField(default=False, verbose_name='خصوصی ')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    text = models.TextField(verbose_name='متن')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_tickets', verbose_name='فرستنده')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_tickets',
                                 verbose_name='دریافت کننده', null=True, blank=True)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, null=True, blank=True, related_name='tickets',
                                  verbose_name='پروژه پرسشگری')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
