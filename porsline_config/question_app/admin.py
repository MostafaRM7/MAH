from django.contrib import admin
from . import models

admin.site.register(models.Questionnaire)
admin.site.register(models.OptionalQuestion)
admin.site.register(models.Option)
admin.site.register(models.TextAnswerQuestion)
admin.site.register(models.DropDownQuestion)
admin.site.register(models.DropDownOption)
admin.site.register(models.IntegerRangeQuestion)
admin.site.register(models.IntegerSelectiveQuestion)
admin.site.register(models.FileQuestion)
admin.site.register(models.NumberAnswerQuestion)
admin.site.register(models.EmailFieldQuestion)
admin.site.register(models.LinkQuestion)
admin.site.register(models.PictureFieldQuestion)
admin.site.register(models.Answer)
admin.site.register(models.AnswerSet)
admin.site.register(models.QuestionGroup)
admin.site.register(models.Folder)

