from django.db.models import Q

from interview_app.models import Interview
from question_app.models import *
from user_app.models import Profile

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

def copy_template_questionnaire(template:Questionnaire, owner:Profile, folder:Folder=None):
    copied_question = None
    groups = {}
    if folder is None:
        folder = Folder.objects.create(name='پیش فرض', owner=owner)
    copied_questionnaire = Questionnaire.objects.create(owner=owner,folder=folder ,**template.to_dict)
    for question in template.questions.filter(~Q(question_type='group')):
        match question.question_type:
            case 'optional':
                optional_question = question.optionalquestion
                copied_question = OptionalQuestion.objects.create(questionnaire=copied_questionnaire, **optional_question.to_dict)
                for option in optional_question.options.all():
                    copied_question.options.create(**option.to_dict)
            case 'drop_down':
                drop_down_question = question.dropdownquestion
                copied_question = DropDownQuestion.objects.create(questionnaire=copied_questionnaire, **drop_down_question.to_dict)
                for option in drop_down_question.options.all():
                    copied_question.options.create(**option.to_dict)
            case 'sort':
                sort_question = question.sortquestion
                copied_question = SortQuestion.objects.create(questionnaire=copied_questionnaire, **sort_question.to_dict)
                for option in sort_question.options.all():
                    copied_question.options.create(**option.to_dict)
            case 'text_answer':
                text_question = question.textanswerquestion
                copied_question = TextAnswerQuestion.objects.create(questionnaire=copied_questionnaire, **text_question.to_dict)
            case 'number_answer':
                number_question = question.numberanswerquestion
                copied_question = NumberAnswerQuestion.objects.create(questionnaire=copied_questionnaire, **number_question.to_dict)
            case 'integer_range':
                integer_range_question = question.integerrangequestion
                copied_question = IntegerRangeQuestion.objects.create(questionnaire=copied_questionnaire, **integer_range_question.to_dict)
            case 'integer_selective':
                integer_selective_question = question.integerselectivequestion
                copied_question = IntegerSelectiveQuestion.objects.create(questionnaire=copied_questionnaire, **integer_selective_question.to_dict)
            case 'email_field':
                email_question = question.emailfieldquestion
                copied_question = EmailFieldQuestion.objects.create(questionnaire=copied_questionnaire, **email_question.to_dict)
            case 'link':
                link_question = question.linkquestion
                copied_question = LinkQuestion.objects.create(questionnaire=copied_questionnaire, **link_question.to_dict)
            case 'file':
                file_question = question.filequestion
                copied_question = FileQuestion.objects.create(questionnaire=copied_questionnaire, **file_question.to_dict)
            case 'no_answer':
                copied_question = NoAnswerQuestion.objects.create(questionnaire=copied_questionnaire, **question.noanswerquestion.to_dict)
        if copied_question:
            if question.group is not None:
                if groups.get(question.group.id) is not None and isinstance(groups.get(question.group.id), list):
                    groups[question.group.id].append(copied_question)
                else:
                    groups[question.group.id] = [copied_question]
    if len(groups.keys()) > 0:
        for group_id in groups.keys():
            group = template.questions.get(id=group_id).groupquestion
            copied_group = QuestionGroup.objects.create(questionnaire=copied_questionnaire, **group.to_dict)
            copied_group.child_questions.set(groups[group_id])

    return copied_questionnaire


def copy_template_interview(template:Interview, owner:Profile, folder:Folder=None):
    copied_question = None
    groups = {}
    if folder is None:
        folder = Folder.objects.create(name='پیش فرض', owner=owner)
    copied_interview = Interview.objects.create(owner=owner,folder=folder ,**template.to_dict, approval_status=Interview.PENDING_PRICE_ADMIN)
    for question in template.questions.filter(~Q(question_type='group')):
        match question.question_type:
            case 'optional':
                optional_question = question.optionalquestion
                copied_question = OptionalQuestion.objects.create(questionnaire=copied_interview, **optional_question.to_dict)
                for option in optional_question.options.all():
                    copied_question.options.create(**option.to_dict)
            case 'drop_down':
                drop_down_question = question.dropdownquestion
                copied_question = DropDownQuestion.objects.create(questionnaire=copied_interview, **drop_down_question.to_dict)
                for option in drop_down_question.options.all():
                    copied_question.options.create(**option.to_dict)
            case 'sort':
                sort_question = question.sortquestion
                copied_question = SortQuestion.objects.create(questionnaire=copied_interview, **sort_question.to_dict)
                for option in sort_question.options.all():
                    copied_question.options.create(**option.to_dict)
            case 'text_answer':
                text_question = question.textanswerquestion
                copied_question = TextAnswerQuestion.objects.create(questionnaire=copied_interview, **text_question.to_dict)
            case 'number_answer':
                number_question = question.numberanswerquestion
                copied_question = NumberAnswerQuestion.objects.create(questionnaire=copied_interview, **number_question.to_dict)
            case 'integer_range':
                integer_range_question = question.integerrangequestion
                copied_question = IntegerRangeQuestion.objects.create(questionnaire=copied_interview, **integer_range_question.to_dict)
            case 'integer_selective':
                integer_selective_question = question.integerselectivequestion
                copied_question = IntegerSelectiveQuestion.objects.create(questionnaire=copied_interview, **integer_selective_question.to_dict)
            case 'email_field':
                email_question = question.emailfieldquestion
                copied_question = EmailFieldQuestion.objects.create(questionnaire=copied_interview, **email_question.to_dict)
            case 'link':
                link_question = question.linkquestion
                copied_question = LinkQuestion.objects.create(questionnaire=copied_interview, **link_question.to_dict)
            case 'file':
                file_question = question.filequestion
                copied_question = FileQuestion.objects.create(questionnaire=copied_interview, **file_question.to_dict)
            case 'no_answer':
                copied_question = NoAnswerQuestion.objects.create(questionnaire=copied_interview, **question.noanswerquestion.to_dict)
        if copied_question:
            if question.group is not None:
                if groups.get(question.group.id) is not None and isinstance(groups.get(question.group.id), list):
                    groups[question.group.id].append(copied_question)
                else:
                    groups[question.group.id] = [copied_question]
            if copied_question.level == 0:
                copied_question.level = 2
                copied_question.save()
    if len(groups.keys()) > 0:
        for group_id in groups.keys():
            group = template.questions.get(id=group_id).groupquestion
            copied_group = QuestionGroup.objects.create(questionnaire=copied_interview, **group.to_dict)
            copied_group.child_questions.set(groups[group_id])
    return copied_interview