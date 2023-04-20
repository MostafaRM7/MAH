from .general_serializers import *
from ..models import *


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('question', 'answer', 'file')

    def validate(self, data):
        answer = data.get('answer')

        return data


class AnswerSetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = AnswerSet
        fields = ('id', 'questionnaire', 'answers')

    def validate(self, data):
        questionnaire = data.get('questionnaire')
        answers = data.get('answers')
        questions = questionnaire.questions.all()
        answered_questions = [answer.get('question') for answer in answers]
        for question in questions:
            if question.questionnaire != questionnaire:
                raise serializers.ValidationError(
                    {'questionnaire': f'Questionnaire does not contain question with id {question.id}'},
                    status.HTTP_400_BAD_REQUEST
                )
            else:
                if question.is_required and question not in answered_questions:
                    raise serializers.ValidationError(
                        {'question': f'Question with id {question.id} is required'},
                        status.HTTP_400_BAD_REQUEST
                    )
                if question.question_type == "optional":
                    optional_question: OptionalQuestion = question.optionalquestion
                    max_selected_options = optional_question.max_selected_options
                    min_selected_options = optional_question.min_selected_options
                    all_options = optional_question.all_options
                    nothing_selected = optional_question.nothing_selected
                    multiple_choice = optional_question.multiple_choice
                    options = optional_question.options.all()
                    options_ids = [option.id for option in options]
                    question_answer = None
                    for answer in answers:
                        if answer.question == question:
                            question_answer = answer
                            break
                    if question_answer is not None:
                        selections = tuple(question_answer.get('selected_options'))
                        selected_count = len(selections)
                        for selection in selections:
                            if selection not in options_ids:
                                raise serializers.ValidationError(
                                    {'question': 'the selected option not belongs to this question'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        if selected_count == 0 and question.is_required and not nothing_selected:
                            raise serializers.ValidationError(
                                {'question': 'you cannot select nothing with is_required true'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        else:
                            if multiple_choice:
                                if selected_count >= 1:
                                    if selected_count > max_selected_options:
                                        raise serializers.ValidationError(
                                            {'question': 'you cannot select more than max_selected_options'},
                                            status.HTTP_400_BAD_REQUEST
                                        )
                                    elif selected_count < min_selected_options:
                                        raise serializers.ValidationError(
                                            {'question': 'you cannot select less than min_selected_options'},
                                            status.HTTP_400_BAD_REQUEST
                                        )

                    else:
                        pass

        return data


@transaction.atomic()
def create(self, validated_data):
    answers_data = validated_data.pop('answers')
    answer_set = AnswerSet.objects.create(**validated_data)
    answers = [Answer(answer_set=answer_set, **answer_data) for answer_data in answers_data]
    Answer.objects.bulk_create(answers)
    return answer_set
