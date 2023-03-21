from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator, MaxValueValidator, MinValueValidator
from uuid import uuid4
from django.db import models


class Folder(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Questionnaire(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    has_timer = models.BooleanField(default=False)
    has_auto_start = models.BooleanField(default=False)
    pub_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    timer = models.PositiveBigIntegerField(null=True, blank=True)  # Recievs seconds
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='questionnaires')
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='questionnaires')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    QUESTION_TYPES = (
        ('optional', 'Optional'),
        ('drop_down', 'Drop Down'),
        ('text_answer', 'Text Answer'),
        ('number_answer', 'Number Answer'),
        ('integer_range', 'Integer Range'),
        ('integer_selective', 'Integer Selective'),
        ('picture_field', 'Picture Field'),
        ('email_field', 'Email Field'),
        ('link', 'Link'),
        ('file', 'File'),
    )
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    media = models.FileField(upload_to='question_media', null=True, blank=True)

    def __str__(self):
        return f'{self.questionnaire} - {self.question_type}'


class OptionalQuestion(Question):
    multiple_choice = models.BooleanField(default=False)
    additional_options = models.BooleanField(default=False)

    # If multiple_choice is True, then max_selected_options and min_selected_options will be used
    max_selected_options = models.IntegerField(null=True, blank=True)
    min_selected_options = models.IntegerField(null=True, blank=True)

    # If additional_options is True, then all_options and nothing_selected will be used
    all_options = models.BooleanField(default=False, null=True, blank=True)
    nothing_selected = models.BooleanField(default=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.multiple_choice:
            self.max_selected_options = None
            self.min_selected_options = None
        if not self.additional_options:
            self.all_options = None
            self.nothing_selected = None
        if self.nothing_selected or self.all_options:
            self.all_options = False
            self.multiple_choice = False
        self.question_type = 'optional'
        super(OptionalQuestion, self).save(*args, **kwargs)


class Option(models.Model):
    optional_question = models.ForeignKey(OptionalQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=250)
    is_selected = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'{self.optional_question} - {self.text}'


class DropDownQuestion(Question):
    multiple_choice = models.BooleanField(default=False)

    # If multiple_choice is True, then max_selected_options and min_selected_options will be used
    max_selected_options = models.PositiveIntegerField(null=True, blank=True)
    min_selected_options = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.multiple_choice:
            self.max_selected_options = None
            self.min_selected_options = None
        self.question_type = 'drop_down'
        super(DropDownQuestion, self).save(*args, **kwargs)


class DropDownOption(models.Model):
    drop_down_question = models.ForeignKey(DropDownQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=250)
    is_selected = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'{self.drop_down_question} - {self.text}'


# TODO - validation should be done in view
# Default ones are set here
class TextAnswerQuestion(Question):
    min = models.PositiveIntegerField(default=10, null=True, blank=True)
    max = models.PositiveIntegerField(default=1000, null=True, blank=True)
    answer = models.TextField(null=True, validators=[
        MinLengthValidator(10),
        MaxLengthValidator(1000)
    ])

    def save(self, *args, **kwargs):
        if self.min > self.max:
            self.min, self.max = self.max, self.min
        self.question_type = 'text_answer'
        super(TextAnswerQuestion, self).save(*args, **kwargs)


# TODO - Float, Negative
# TODO - validation should be done in view
# Default ones are set here
class NumberAnswerQuestion(Question):
    min = models.IntegerField(default=0, null=True, blank=True)
    max = models.IntegerField(default=1000, null=True, blank=True)
    answer = models.IntegerField(null=True, validators=[
        MinValueValidator(0),
        MaxValueValidator(1000)
    ])

    def save(self, *args, **kwargs):
        if self.min > self.max:
            self.min, self.max = self.max, self.min
        self.question_type = 'number_answer'
        super(NumberAnswerQuestion, self).save(*args, **kwargs)


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
    answer = models.PositiveIntegerField(null=True, blank=True, validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])

    def save(self, *args, **kwargs):
        self.question_type = 'integer_range'
        super(IntegerRangeQuestion, self).save(*args, **kwargs)


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
    answer = models.PositiveIntegerField(validators=[
        MaxValueValidator(5)
    ])

    def save(self, *args, **kwargs):
        self.question_type = 'integer_selective'
        super(IntegerSelectiveQuestion, self).save(*args, **kwargs)


class PictureFieldQuestion(Question):
    answer = models.ImageField(null=True, blank=True, upload_to='images/')

    def save(self, *args, **kwargs):
        self.question_type = 'picture_field'
        super(PictureFieldQuestion, self).save(*args, **kwargs)


class EmailFieldQuestion(Question):
    answer = models.EmailField(default='', null=True, blank=True, max_length=255)

    def save(self, *args, **kwargs):
        self.question_type = 'email_field'
        super(EmailFieldQuestion, self).save(*args, **kwargs)


class LinkQuestion(Question):
    answer = models.URLField(null=True, blank=True, max_length=255)

    def save(self, *args, **kwargs):
        self.question_type = 'link'
        super(LinkQuestion, self).save(*args, **kwargs)


class FileQuestion(Question):
    answer = models.FileField(null=True, blank=True, upload_to='files/')
    max_volume = models.PositiveIntegerField(default=5, null=True, blank=True)  # In MB

    def save(self, *args, **kwargs):
        self.question_type = 'file'
        super(FileQuestion, self).save(*args, **kwargs)
