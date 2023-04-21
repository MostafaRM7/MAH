from django.contrib.auth import get_user_model
from django.db import models
from uuid import uuid4


class Folder(models.Model):
    owner = models.ForeignKey(get_user_model(), default=None, null=True, on_delete=models.CASCADE,
                              related_name='folders')
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
    timer = models.DurationField(null=True, blank=True)
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
        ('group', 'Group'),
    )
    title = models.CharField(max_length=255)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    media = models.FileField(upload_to='uploads/question_media', null=True, blank=True)

    def __str__(self):
        return f'{self.questionnaire} - {self.question_type}'


class OptionalQuestion(Question):
    multiple_choice = models.BooleanField(default=False)
    additional_options = models.BooleanField(default=False)
    max_selected_options = models.IntegerField(null=True, blank=True)
    min_selected_options = models.IntegerField(null=True, blank=True)
    all_options = models.BooleanField(default=False, null=True, blank=True)
    nothing_selected = models.BooleanField(default=False, null=True, blank=True)

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


class TextAnswerQuestion(Question):
    PATTERNS = (
        ('free', 'Free Text'),
        ('jalali_date', 'Jalali Date'),
        ('gregorian_date', 'Gregorian Date'),
        ('mobile_number', 'Mobile Number'),
        ('phone_number', 'Phone Number'),
        ('number_character', 'Number Character'),
        ('persian_letters', 'Persian Letters'),
        ('english_letters', 'English Letters')

    )
    pattern = models.CharField(max_length=50, choices=PATTERNS, default='free')
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
    answer = models.ImageField(null=True, blank=True, upload_to='images/')

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
