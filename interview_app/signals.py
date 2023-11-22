from django.db.models.signals import post_save
from django.dispatch import receiver

from question_app.models import OptionalQuestion, DropDownQuestion, SortQuestion, TextAnswerQuestion, \
    NumberAnswerQuestion, IntegerRangeQuestion, IntegerSelectiveQuestion, EmailFieldQuestion, LinkQuestion, FileQuestion


@receiver(post_save, sender=OptionalQuestion)
def question_created(sender, instance: OptionalQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()

@receiver(post_save, sender=DropDownQuestion)
def question_created(sender, instance: DropDownQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=SortQuestion)
def question_created(sender, instance: SortQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=TextAnswerQuestion)
def question_created(sender, instance: TextAnswerQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=NumberAnswerQuestion)
def question_created(sender, instance: NumberAnswerQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=IntegerRangeQuestion)
def question_created(sender, instance: IntegerRangeQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=IntegerSelectiveQuestion)
def question_created(sender, instance: IntegerSelectiveQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=EmailFieldQuestion)
def question_created(sender, instance: EmailFieldQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=LinkQuestion)
def question_created(sender, instance: LinkQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()


@receiver(post_save, sender=FileQuestion)
def question_created(sender, instance: FileQuestion, created, **kwargs):
    print('question_created')
    if not created:
        instance.level = 0
        instance.save()
