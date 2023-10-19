from django.db.models.signals import post_save
from django.dispatch import receiver

from question_app.models import Question


@receiver(post_save, sender=Question)
def question_created(sender, instance: Question, created, **kwargs):
    if created:
        answer_sets = instance.questionnaire.answer_sets
        if answer_sets.exists():
            if not answer_sets.filter(answers__question_id=instance.id).exists():
                for answer_set in answer_sets.all():
                    answer_set.answers.create(question=instance)

