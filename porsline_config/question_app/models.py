from uuid import uuid4
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models


class Folder(models.Model):
    owner = models.ForeignKey(get_user_model(), default=None, null=True, on_delete=models.CASCADE,
                              related_name='folders')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Questionnaire(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    has_timer = models.BooleanField(default=False)
    has_auto_start = models.BooleanField(default=False)
    pub_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    timer = models.DurationField(null=True, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='questionnaires')
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='questionnaires')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
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
    )

    placement = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    media = models.FileField(upload_to='uploads/question_media', null=True, blank=True,
                             validators=[FileExtensionValidator(ALLOWED_MEDIA_EXTENSIONS)])
    show_number = models.BooleanField(null=True, blank=True, default=True)
    group = models.ForeignKey('QuestionGroup', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='child_questions')

    def clean(self):
        super().clean()
        if self.media.size > 1024 * 1024 * 10:
            raise ValidationError('حجم فایل آپلود شده باید کمتر از ۱۰ مگابایت باشد')

    def __str__(self):
        return f'{self.questionnaire} - {self.question_type}'


class OptionalQuestion(Question):
    multiple_choice = models.BooleanField(default=False)
    additional_options = models.BooleanField(default=False)
    max_selected_options = models.IntegerField(null=True, blank=True)
    min_selected_options = models.IntegerField(null=True, blank=True)
    all_options = models.BooleanField(default=False, null=True, blank=True)
    nothing_selected = models.BooleanField(default=False, null=True, blank=True)
    is_vertical = models.BooleanField(default=False, null=True, blank=True)
    is_random_options = models.BooleanField(default=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.question_type = 'optional'
        super(OptionalQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class Option(models.Model):
    optional_question = models.ForeignKey(OptionalQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.optional_question} - {self.text}'


class DropDownQuestion(Question):
    multiple_choice = models.BooleanField(default=False)
    max_selected_options = models.PositiveIntegerField(null=True, blank=True)
    min_selected_options = models.PositiveIntegerField(null=True, blank=True)
    is_alphabetic_order = models.BooleanField(default=False, null=True, blank=True)
    is_random_options = models.BooleanField(default=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.question_type = 'drop_down'
        super(DropDownQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class DropDownOption(models.Model):
    drop_down_question = models.ForeignKey(DropDownQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.drop_down_question} - {self.text}'


class SortQuestion(Question):
    is_random_options = models.BooleanField(default=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.question_type = 'sort'
        super(SortQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class SortOption(models.Model):
    sort_question = models.ForeignKey('SortQuestion', on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=250)
    placement = models.PositiveIntegerField()


class TextAnswerQuestion(Question):
    FREE = 'free'
    JALALI_DATE = 'jalali_date'
    GEORGIAN_DATE = 'gregorian_date'
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
    pattern = models.CharField(max_length=50, choices=PATTERNS, default=FREE)
    min = models.PositiveIntegerField(default=10, null=True, blank=True)
    max = models.PositiveIntegerField(default=1000, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.question_type = 'text_answer'
        super(TextAnswerQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class NumberAnswerQuestion(Question):
    min = models.IntegerField(default=0, null=True, blank=True)
    max = models.IntegerField(default=1000, null=True, blank=True)

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
    min = models.PositiveIntegerField(choices=MIN_CHOICES, default=ONE_CHOICE, null=True, blank=True)
    max = models.PositiveIntegerField(default=5, null=True, blank=True)
    min_label = models.CharField(max_length=50, null=True, blank=True)
    mid_label = models.CharField(max_length=50, null=True, blank=True)
    max_label = models.CharField(max_length=50, null=True, blank=True)

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
    shape = models.CharField(choices=STYLE_CHOICES, default=STAR, max_length=2)
    max = models.PositiveIntegerField(default=5, null=True, blank=True)

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
    max_volume = models.PositiveIntegerField(default=5, null=True, blank=True)  # In MB

    def save(self, *args, **kwargs):
        self.question_type = 'file'
        super(FileQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_text


class AnswerSet(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='answer_set')

    def __str__(self):
        return f'{self.questionnaire} - AnswerSet'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_set = models.ForeignKey(AnswerSet, on_delete=models.CASCADE, related_name='answers')
    answer = models.JSONField()
    file = models.FileField(upload_to='files/', null=True, blank=True)

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
    button_shape = models.CharField(max_length=6, choices=BUTTON_SHAPES, default=ROUND)
    button_text = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.is_required = False
        self.question_type = 'group'
        super(QuestionGroup, self).save(*args, **kwargs)


class WelcomePage(models.Model):
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
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    media = models.FileField(upload_to='welcome_page/medias', null=True, blank=True,
                             validators=[FileExtensionValidator(ALLOWED_MEDIA_EXTENSIONS)])
    button_text = models.CharField(max_length=100)
    button_shape = models.CharField(max_length=6, choices=BUTTON_SHAPES, default=ROUND)
    questionnaire = models.OneToOneField(Questionnaire, on_delete=models.CASCADE, related_name='welcome_page')


class ThanksPage(models.Model):
    ALLOWED_MEDIA_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv',
                                'mkv', 'webm']
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    media = models.FileField(upload_to='thanks_page/medias', null=True, blank=True,
                             validators=[FileExtensionValidator(ALLOWED_MEDIA_EXTENSIONS)])
    share_link = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    whatsapp = models.URLField(null=True, blank=True)
    eitaa = models.URLField(null=True, blank=True)
    sorush = models.URLField(null=True, blank=True)
    questionnaire = models.OneToOneField(Questionnaire, on_delete=models.CASCADE, related_name='thanks_page')
