from uuid import uuid4
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models


class Folder(models.Model):
    owner = models.ForeignKey(get_user_model(), default=None, null=True, on_delete=models.SET_NULL,
                              related_name='folders', verbose_name='صاحب')
    name = models.CharField(max_length=255, verbose_name='نام')

    def __str__(self):
        return self.name


class Questionnaire(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام')
    is_active = models.BooleanField(default=False, verbose_name='فعال/غیرفعال')
    is_delete = models.BooleanField(default=False, verbose_name='حذف شده/نشده')
    pub_date = models.DateField(null=True, blank=True, auto_now_add=True, verbose_name='تاریخ انتشار')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاریخ پایان')
    timer = models.DurationField(null=True, blank=True, verbose_name='تایمر')
    show_question_in_pages = models.BooleanField(default=True, verbose_name='نشان دادن سوال ها در صفحات مجزا')
    progress_bar = models.BooleanField(default=True, verbose_name='نشان دادن نوار پیشرفت')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, related_name='questionnaires', null=True, blank=True,
                               verbose_name='پوشه')
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL,
                              related_name='questionnaires', null=True, verbose_name='صاحب')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name='یو یو آی دی')

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()


class Question(models.Model):
    ALLOWED_MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv',
                                'mkv', 'webm']  # TODO - formats?
    QUESTION_TYPES = (
        ('optional', 'Optional'),
        ('drop_down', 'Drop Down'),
        ('sort', 'Sort'),
        ('text_answer', 'Text Answer'),
        ('number_answer', 'Number Answer'),
        ('integer_range', 'Integer Range'),
        ('integer_selective', 'Integer Selective'),
        ('picture_field', 'Picture Field'),
        ('email_field', 'Email Field'),
        ('link', 'Link'),
        ('file', 'File'),
        ('group', 'Group'),
    )

    placement = models.PositiveIntegerField(null=True, blank=True, verbose_name='جایگاه')
    title = models.CharField(max_length=255, verbose_name='عنوان')
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions',
                                      verbose_name='پرسشنامه')
    question_text = models.TextField(verbose_name='متن سوال')
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, editable=False, verbose_name='نوع سوال')
    is_required = models.BooleanField(default=False, verbose_name='اجباری/عیراجباری')
    media = models.FileField(upload_to='question_media/%Y/%m/%d', null=True, blank=True,
                             validators=[FileExtensionValidator(ALLOWED_MEDIA_EXTENSIONS)],
                             verbose_name='تصویر یا فیلم')
    show_number = models.BooleanField(default=True, verbose_name='نمایش شماره سوال')
    group = models.ForeignKey('QuestionGroup', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='child_questions', verbose_name='گروه')

    class Meta:
        ordering = ('placement',)

    def clean(self):
        super().clean()
        try:
            if self.media.size > 1024 * 1024 * 10:
                raise ValidationError('حجم فایل آپلود شده باید کمتر از ۱۰ مگابایت باشد')
        except ValueError:
            pass

    def __str__(self):
        return f'{self.questionnaire} - {self.question_type}'


class OptionalQuestion(Question):
    multiple_choice = models.BooleanField(default=False, verbose_name='چند انتخابی')
    additional_options = models.BooleanField(default=False, verbose_name='گزینه های اضافی')
    max_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر گزینه انتخابی')
    min_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداقل گزینه انتخابی')
    all_options = models.BooleanField(default=False, null=True, blank=True, verbose_name='انتخاب همه گزینه ها')
    nothing_selected = models.BooleanField(default=False, null=True, blank=True, verbose_name='هیچ کدام')
    is_vertical = models.BooleanField(default=False, null=True, blank=True, verbose_name='نمایش عمودی گزینه ها')
    is_random_options = models.BooleanField(default=False, null=True, blank=True, verbose_name='ترتیب تصادفی گزینه ها')

    def save(self, *args, **kwargs):
        self.question_type = 'optional'
        super(OptionalQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class Option(models.Model):
    optional_question = models.ForeignKey(OptionalQuestion, on_delete=models.CASCADE, related_name='options',
                                          verbose_name='سوال چند گزینه ای ')
    text = models.CharField(max_length=250, verbose_name='متن گزینه')

    def __str__(self):
        return f'{self.optional_question} - {self.text}'


class DropDownQuestion(Question):
    multiple_choice = models.BooleanField(default=False, verbose_name='چند انتخابی')
    max_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر گزینه انتخابی')
    min_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداقل گزینه انتخابی')
    is_alphabetic_order = models.BooleanField(default=False, verbose_name='مرتب سازی بر اساس حروف الفبا')
    is_random_options = models.BooleanField(default=False, verbose_name='ترتیب تصادفی گزینه ها')

    def save(self, *args, **kwargs):
        self.question_type = 'drop_down'
        super(DropDownQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class DropDownOption(models.Model):
    drop_down_question = models.ForeignKey(DropDownQuestion, on_delete=models.CASCADE, related_name='options',
                                           verbose_name='سوال کشویی')
    text = models.CharField(max_length=250, verbose_name='متن گزینه')

    def __str__(self):
        return f'{self.drop_down_question} - {self.text}'


class SortQuestion(Question):
    is_random_options = models.BooleanField(default=False, verbose_name='ترتیب تصادفی گزینه ها')

    def save(self, *args, **kwargs):
        self.question_type = 'sort'
        super(SortQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class SortOption(models.Model):
    sort_question = models.ForeignKey('SortQuestion', on_delete=models.CASCADE, related_name='options',
                                      verbose_name='سوال اولویت دهی')
    text = models.CharField(max_length=250, verbose_name='متن گزینه')


class TextAnswerQuestion(Question):
    FREE = 'free'
    JALALI_DATE = 'jalali_date'
    GEORGIAN_DATE = 'georgian_date'
    MOBILE_NUMBER = 'mobile_number'
    PHONE_NUMBER = 'phone_number'
    NUMBER_CHARACTERS = 'number_character'
    PERSIAN_LETTERS = 'persian_letters'
    ENGLISH_LETTERS = 'english_letters'
    PATTERNS = (
        (FREE, 'Free Text'),
        (JALALI_DATE, 'Jalali Date'),
        (GEORGIAN_DATE, 'Gregorian Date'),
        (MOBILE_NUMBER, 'Mobile Number'),
        (PHONE_NUMBER, 'Phone Number'),
        (NUMBER_CHARACTERS, 'Number Character'),
        (PERSIAN_LETTERS, 'Persian Letters'),
        (ENGLISH_LETTERS, 'English Letters')

    )
    answer_template = models.CharField(max_length=250, null=True, blank=True, verbose_name='قالب پاسخ')
    pattern = models.CharField(max_length=50, choices=PATTERNS, default=FREE, verbose_name='الگوی پاسخ')
    min = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداقل طول جواب')
    max = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر طول جواب')

    def save(self, *args, **kwargs):
        self.question_type = 'text_answer'
        super(TextAnswerQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class NumberAnswerQuestion(Question):
    min = models.IntegerField(null=True, blank=True, verbose_name='حداقل مقدار')
    max = models.IntegerField(null=True, blank=True, verbose_name='حداکثر مقدار')

    def save(self, *args, **kwargs):
        self.question_type = 'number_answer'
        super(NumberAnswerQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class IntegerRangeQuestion(Question):
    ZERO_CHOICE = 0
    ONE_CHOICE = 1
    MIN_CHOICES = [
        (ZERO_CHOICE, '1'),
        (ONE_CHOICE, '0'),
    ]
    min = models.PositiveIntegerField(choices=MIN_CHOICES, default=ONE_CHOICE, verbose_name='حداقل مقدار')
    max = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر مقدار')
    min_label = models.CharField(max_length=50, null=True, blank=True, verbose_name='برچسب چپ')
    mid_label = models.CharField(max_length=50, null=True, blank=True, verbose_name='برچسب وسط')
    max_label = models.CharField(max_length=50, null=True, blank=True, verbose_name='برچسب راست')

    def save(self, *args, **kwargs):
        self.question_type = 'integer_range'
        super(IntegerRangeQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class IntegerSelectiveQuestion(Question):
    HEART = 'H'
    STAR = 'S'
    LIKE = 'L'
    CHECK_MARK = 'C'
    STYLE_CHOICES = [
        (HEART, 'Heart'),
        (STAR, 'Star'),
        (LIKE, 'Like'),
        (CHECK_MARK, 'Check Mark'),
    ]
    shape = models.CharField(choices=STYLE_CHOICES, default=STAR, max_length=2, verbose_name='شکل دکمه')
    max = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر مقدار')

    def save(self, *args, **kwargs):
        self.question_type = 'integer_selective'
        super(IntegerSelectiveQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class PictureFieldQuestion(Question):

    def save(self, *args, **kwargs):
        self.question_type = 'picture_field'
        super(PictureFieldQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class EmailFieldQuestion(Question):
    def save(self, *args, **kwargs):
        self.question_type = 'email_field'
        super(EmailFieldQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class LinkQuestion(Question):

    def save(self, *args, **kwargs):
        self.question_type = 'link'
        super(LinkQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class FileQuestion(Question):
    max_volume = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر حجم')

    def save(self, *args, **kwargs):
        self.question_type = 'file'
        super(FileQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class AnswerSet(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT,
                                      related_name='answer_set', verbose_name='پرسشنامه')

    def __str__(self):
        return f'{self.questionnaire} - AnswerSet'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='سوال')
    answer_set = models.ForeignKey(AnswerSet, on_delete=models.CASCADE, related_name='answers',
                                   verbose_name='دسته جواب')
    answer = models.JSONField(verbose_name='جواب')
    file = models.FileField(upload_to='answer_file/%Y/%m/%d', null=True, blank=True, verbose_name='فایل')

    def __str__(self):
        return f'{self.answer_set} - {self.question}'


class QuestionGroup(Question):
    SHARP = 'sharp'
    ROUND = 'round'
    OVAL = 'oval'
    BUTTON_SHAPES = (
        (SHARP, 'Sharp corners'),
        (ROUND, 'Round corners'),
        (OVAL, 'Oval')
    )
    button_shape = models.CharField(max_length=6, choices=BUTTON_SHAPES, default=ROUND, verbose_name='شکل دکمه')
    is_solid_button = models.BooleanField(default=False, verbose_name='دکمه تو پر/تو خالی')
    button_text = models.CharField(max_length=100, verbose_name='متن دکمه')

    def save(self, *args, **kwargs):
        self.is_required = False
        self.question_type = 'group'
        super(QuestionGroup, self).save(*args, **kwargs)


class WelcomePage(models.Model):
    ALLOWED_MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv',
                                'mkv', 'webm']  # TODO asking from ui/ux
    SHARP = 'sharp'
    ROUND = 'round'
    OVAL = 'oval'
    BUTTON_SHAPES = (
        (SHARP, 'Sharp corners'),
        (ROUND, 'Round corners'),
        (OVAL, 'Oval')
    )
    title = models.CharField(max_length=255, verbose_name='عنوان')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')
    media = models.FileField(upload_to='welcome_page/%Y/%m/%d', null=True, blank=True,
                             validators=[FileExtensionValidator(ALLOWED_MEDIA_EXTENSIONS)],
                             verbose_name='تصویر یا فیلم')
    is_solid_button = models.BooleanField(default=False, verbose_name='دکمه تو پر/تو خالی')
    button_text = models.CharField(max_length=100, verbose_name='متن دکمه')
    button_shape = models.CharField(max_length=6, choices=BUTTON_SHAPES, default=ROUND, verbose_name='شکل دکمه')
    questionnaire = models.OneToOneField(Questionnaire, on_delete=models.CASCADE, related_name='welcome_page',
                                         verbose_name='پرسشنامه')


class ThanksPage(models.Model):
    ALLOWED_MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv',
                                'mkv', 'webm']  # TODO asking from ui/ux
    title = models.CharField(max_length=255, verbose_name='عنوان')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')
    media = models.FileField(upload_to='thanks_page/%Y/%m/%d', null=True, blank=True,
                             validators=[FileExtensionValidator(ALLOWED_MEDIA_EXTENSIONS)],
                             verbose_name='تصویر یا فیلم')
    share_link = models.BooleanField(default=False, verbose_name='اشتراک گذاری لینک')
    instagram = models.BooleanField(default=False, verbose_name='اشتراک در اینستاگرام')
    telegram = models.BooleanField(default=False, verbose_name='اشتراک در تلگرام')
    whatsapp = models.BooleanField(default=False, verbose_name='اشتراک در واتساپ')
    eitaa = models.BooleanField(default=False, verbose_name='اشتراک در ایتا')
    sorush = models.BooleanField(default=False, verbose_name='اشتراک در سروش')
    questionnaire = models.OneToOneField(Questionnaire, on_delete=models.CASCADE, related_name='thanks_page',
                                         verbose_name='پرسشنامه')
