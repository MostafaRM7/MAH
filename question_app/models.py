from uuid import uuid4
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.db import models
from admin_app.models import PricePack
from user_app.models import Profile, District


class Folder(models.Model):
    owner = models.ForeignKey(Profile, default=None, null=True, on_delete=models.SET_NULL,
                              related_name='folders', verbose_name='صاحب')
    name = models.CharField(max_length=255, verbose_name='نام')

    def __str__(self):
        return self.name


class Questionnaire(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام')
    is_delete = models.BooleanField(default=False, verbose_name='حذف شده/نشده')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیرفعال')
    pub_date = models.DateTimeField(verbose_name='تاریخ انتشار', null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پایان')
    timer = models.DurationField(null=True, blank=True, verbose_name='تایمر')
    previous_button = models.BooleanField(default=False, verbose_name='نمایش دکمه قبلی')
    show_question_in_pages = models.BooleanField(default=True, verbose_name='نشان دادن سوال ها در صفحات مجزا')
    progress_bar = models.BooleanField(default=True, verbose_name='نشان دادن نوار پیشرفت')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, related_name='questionnaires', null=True, blank=True,
                               verbose_name='پوشه')
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL,
                              related_name='questionnaires', null=True, verbose_name='صاحب')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name='یو یو آی دی')
    show_number = models.BooleanField(default=True, verbose_name='نمایش شماره سوال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد', editable=False)
    bate_questions = ArrayField(models.PositiveIntegerField(), null=True, blank=True)
    price_pack = models.ForeignKey(PricePack, on_delete=models.CASCADE, verbose_name='بسته قیمت',
                                   related_name='interviews', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, blank=True)
    is_template = models.BooleanField(default=False, verbose_name='قالب/غیرقالب')
    is_private = models.BooleanField(default=False, verbose_name='خصوصی ')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def to_dict(self):
        return {
            'name': self.name + ' - کپی',
            'is_active': self.is_active,
            'previous_button': self.previous_button,
            'pub_date': self.pub_date,
            'end_date': self.end_date,
            'timer': self.timer,
            'show_question_in_pages': self.show_question_in_pages,
            'created_at': self.created_at,
            'progress_bar': self.progress_bar,
            'show_number': self.show_number,
            'category': self.category.id if self.category else None
        }

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()

    @property
    def level(self):
        return sum([question.level for question in self.questions.all()])


class Question(models.Model):
    LEVEL_CHOICES = (
        (1, 'آسان'),
        (2, 'متوسط'),
        (3, 'سخت'),
        (0, 'تعیین سطح نشده')
    )
    ALLOWED_MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv',
                                'mkv', 'webm']
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
        ('no_answer', 'No Answer')
    )
    placement = models.PositiveIntegerField(null=True, blank=True, verbose_name='جایگاه')
    title = models.CharField(max_length=255, verbose_name='عنوان')
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions',
                                      verbose_name='پرسشنامه')
    description = models.TextField(verbose_name='متن سوال', null=True, blank=True)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, editable=False, verbose_name='نوع سوال')
    is_required = models.BooleanField(default=False, verbose_name='اجباری/عیراجباری')
    is_finalized = models.BooleanField(default=False, verbose_name='نهایی شده/نشده')
    media = models.FileField(upload_to='question_media/%Y/%m/%d', null=True, blank=True,
                             validators=[FileExtensionValidator(ALLOWED_MEDIA_EXTENSIONS)],
                             verbose_name='تصویر یا فیلم')
    double_picture_size = models.BooleanField(default=False, verbose_name='اندازه تصویر دو برابر')
    group = models.ForeignKey('QuestionGroup', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='child_questions', verbose_name='گروه')
    level = models.PositiveIntegerField(verbose_name='سطح', choices=LEVEL_CHOICES, default=0)

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
    URL_PREFIX = 'optional-questions'
    multiple_choice = models.BooleanField(default=False, verbose_name='چند انتخابی')
    additional_options = models.BooleanField(default=False, verbose_name='گزینه های اضافی')
    max_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر گزینه انتخابی')
    min_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداقل گزینه انتخابی')
    all_options = models.BooleanField(default=False, verbose_name='انتخاب همه گزینه ها')
    nothing_selected = models.BooleanField(default=False, verbose_name='هیچ کدام')
    other_options = models.BooleanField(default=False, verbose_name='گزینه های دیگر')
    is_vertical = models.BooleanField(default=False, verbose_name='نمایش عمودی گزینه ها')
    is_random_options = models.BooleanField(default=False, verbose_name='ترتیب تصادفی گزینه ها')

    def save(self, *args, **kwargs):
        self.question_type = 'optional'
        super(OptionalQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'multiple_choice': self.multiple_choice,
            'additional_options': self.additional_options,
            'max_selected_options': self.max_selected_options,
            'min_selected_options': self.min_selected_options,
            'all_options': self.all_options,
            'nothing_selected': self.nothing_selected,
            'other_options': self.other_options,
            'is_vertical': self.is_vertical,
            'is_random_options': self.is_random_options
        }


class Option(models.Model):
    optional_question = models.ForeignKey(OptionalQuestion, on_delete=models.CASCADE, related_name='options',
                                          verbose_name='سوال چند گزینه ای ')
    text = models.CharField(max_length=250, verbose_name='متن گزینه')
    number = models.PositiveIntegerField(null=True, blank=True, verbose_name='شماره گزینه')

    def __str__(self):
        return f'{self.optional_question} - {self.text}'

    @property
    def to_dict(self):
        return {
            'text': self.text,
            'number': self.number
        }


class DropDownQuestion(Question):
    URL_PREFIX = 'dropdown-questions'
    multiple_choice = models.BooleanField(default=False, verbose_name='چند انتخابی')
    max_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر گزینه انتخابی')
    min_selected_options = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداقل گزینه انتخابی')
    is_alphabetic_order = models.BooleanField(default=False, verbose_name='مرتب سازی بر اساس حروف الفبا')
    is_random_options = models.BooleanField(default=False, verbose_name='ترتیب تصادفی گزینه ها')

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'multiple_choice': self.multiple_choice,
            'max_selected_options': self.max_selected_options,
            'min_selected_options': self.min_selected_options,
            'is_alphabetic_order': self.is_alphabetic_order,
            'is_random_options': self.is_random_options
        }

    def save(self, *args, **kwargs):
        self.question_type = 'drop_down'
        super(DropDownQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class DropDownOption(models.Model):
    drop_down_question = models.ForeignKey(DropDownQuestion, on_delete=models.CASCADE, related_name='options',
                                           verbose_name='سوال کشویی')
    text = models.CharField(max_length=250, verbose_name='متن گزینه')

    @property
    def to_dict(self):
        return {
            'text': self.text
        }

    def __str__(self):
        return f'{self.drop_down_question} - {self.text}'


class SortQuestion(Question):
    URL_PREFIX = 'sort-questions'
    is_random_options = models.BooleanField(default=False, verbose_name='ترتیب تصادفی گزینه ها')

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'is_random_options': self.is_random_options
        }

    def save(self, *args, **kwargs):
        self.question_type = 'sort'
        super(SortQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class SortOption(models.Model):
    sort_question = models.ForeignKey('SortQuestion', on_delete=models.CASCADE, related_name='options',
                                      verbose_name='سوال اولویت دهی')
    text = models.CharField(max_length=250, verbose_name='متن گزینه')

    @property
    def to_dict(self):
        return {
            'text': self.text
        }


class TextAnswerQuestion(Question):
    URL_PREFIX = 'textanswer-questions'
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

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'answer_template': self.answer_template,
            'pattern': self.pattern,
            'min': self.min,
            'max': self.max
        }

    def save(self, *args, **kwargs):
        self.question_type = 'text_answer'
        super(TextAnswerQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class NumberAnswerQuestion(Question):
    URL_PREFIX = 'numberanswer-questions'
    min = models.IntegerField(null=True, blank=True, verbose_name='حداقل مقدار')
    max = models.IntegerField(null=True, blank=True, verbose_name='حداکثر مقدار')
    accept_negative = models.BooleanField(default=True, verbose_name='جواب می تواند منفی باشد')
    accept_float = models.BooleanField(default=True, verbose_name='جواب می تواند اعشاری باشد')

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'min': self.min,
            'max': self.max,
            'accept_negative': self.accept_negative,
            'accept_float': self.accept_float
        }

    def save(self, *args, **kwargs):
        self.is_required = False
        self.question_type = 'number_answer'
        super(NumberAnswerQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class IntegerRangeQuestion(Question):
    URL_PREFIX = 'integerrange-questions'
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

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'min': self.min,
            'max': self.max,
            'min_label': self.min_label,
            'mid_label': self.mid_label,
            'max_label': self.max_label
        }

    def save(self, *args, **kwargs):
        self.question_type = 'integer_range'
        super(IntegerRangeQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class IntegerSelectiveQuestion(Question):
    URL_PREFIX = 'integerselective-questions'
    HEART = 'H'
    STAR = 'S'
    LIKE = 'L'
    DISLIKE = 'D'
    SMILE = 'SM'
    CHECK_MARK = 'C'
    STYLE_CHOICES = [
        (HEART, 'Heart'),
        (STAR, 'Star'),
        (LIKE, 'Like'),
        (CHECK_MARK, 'Check Mark'),
        (DISLIKE, 'Dislike'),
        (SMILE, 'Smile'),
    ]
    shape = models.CharField(choices=STYLE_CHOICES, default=STAR, max_length=2, verbose_name='شکل دکمه')
    max = models.PositiveIntegerField(null=True, blank=True, verbose_name='حداکثر مقدار')

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'shape': self.shape,
            'max': self.max
        }

    def save(self, *args, **kwargs):
        self.question_type = 'integer_selective'
        super(IntegerSelectiveQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class PictureFieldQuestion(Question):

    def save(self, *args, **kwargs):
        self.question_type = 'picture_field'
        super(PictureFieldQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class EmailFieldQuestion(Question):
    URL_PREFIX = 'email-questions'

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement
        }

    def save(self, *args, **kwargs):
        self.question_type = 'email_field'
        super(EmailFieldQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class LinkQuestion(Question):
    URL_PREFIX = 'link-questions'

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement
        }

    def save(self, *args, **kwargs):
        self.question_type = 'link'
        super(LinkQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class FileQuestion(Question):
    mega_byte = 'mb'
    kilo_byte = 'kb'
    UNIT_CHOICES = (
        (mega_byte, 'MB'),
        (kilo_byte, 'KB'),
    )
    URL_PREFIX = 'file-questions'
    max_volume = models.PositiveIntegerField(default=30, verbose_name='حداکثر حجم')
    volume_unit = models.CharField(max_length=3, default=mega_byte, choices=UNIT_CHOICES, verbose_name='واحد حجم')

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'max_volume': self.max_volume,
            'volume_unit': self.volume_unit
        }

    def save(self, *args, **kwargs):
        self.question_type = 'file'
        super(FileQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


# TODO add answered where to answer set for interviews
class AnswerSet(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT,
                                      related_name='answer_sets', verbose_name='پرسشنامه')
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان پاسخگویی')
    answered_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='answer_sets', null=True,
                                    blank=True)

    def __str__(self):
        return f'{self.questionnaire} - AnswerSet'


class Answer(models.Model):
    LEVEL_CHOICES = (
        (0, 'تعیین نشده'),
        (1, 'ساده'),
        (2, 'متوسط'),
        (3, 'سخت'),
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='سوال')
    answer_set = models.ForeignKey(AnswerSet, on_delete=models.CASCADE, related_name='answers',
                                   verbose_name='دسته جواب')
    answer = models.JSONField(verbose_name='جواب', null=True, blank=True)
    file = models.FileField(upload_to='answer_file/%Y/%m/%d', null=True, blank=True, verbose_name='فایل')
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان پاسخگویی')
    level = models.PositiveIntegerField(default=0, choices=LEVEL_CHOICES, verbose_name='سطح')

    def __str__(self):
        return f'{self.answer_set} - {self.question}'


class QuestionGroup(Question):
    URL_PREFIX = 'question-groups'

    # SHARP = 'sharp'
    # ROUND = 'round'
    # OVAL = 'oval'
    # BUTTON_SHAPES = (
    #     (SHARP, 'Sharp corners'),
    #     (ROUND, 'Round corners'),
    #     (OVAL, 'Oval')
    # )
    # button_shape = models.CharField(max_length=6, choices=BUTTON_SHAPES, default=ROUND, verbose_name='شکل دکمه')
    # is_solid_button = models.BooleanField(default=False, verbose_name='دکمه تو پر/تو خالی')
    # button_text = models.CharField(max_length=100, verbose_name='متن دکمه')

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement
        }

    def save(self, *args, **kwargs):
        self.is_required = False
        self.question_type = 'group'
        super(QuestionGroup, self).save(*args, **kwargs)


class NoAnswerQuestion(Question):
    URL_PREFIX = 'noanswer-questions'
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

    @property
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'is_finalized': self.is_finalized,
            'media': self.media,
            'double_picture_size': self.double_picture_size,
            'group': self.group,
            'level': self.level,
            'placement': self.placement,
            'button_shape': self.button_shape,
            'is_solid_button': self.is_solid_button,
            'button_text': self.button_text
        }

    def save(self, *args, **kwargs):
        self.is_required = False
        self.question_type = 'no_answer'
        super(NoAnswerQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class WelcomePage(models.Model):
    URL_PREFIX = 'welcome-pages'
    ALLOWED_MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv',
                                'mkv', 'webm']
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
    URL_PREFIX = 'thanks-pages'
    ALLOWED_MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv',
                                'mkv', 'webm']
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


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام')
