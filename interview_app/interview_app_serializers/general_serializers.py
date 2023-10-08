from interview_app.models import Interview
from question_app.question_app_serializers.question_serializers import NoGroupQuestionSerializer
from result_app import serializers


class InterviewSerializer(serializers.ModelSerializer):
    questions = NoGroupQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Interview
        fields = (
            'id', 'name', 'is_active', 'previous_button', 'pub_date', 'end_date', 'timer',
            'show_question_in_pages', 'created_at', 'progress_bar', 'show_number',
            'folder', 'owner', 'uuid', 'questions', 'pay_per_answer', 'interviewers', 'approval_status',
            'add_to_approve_queue', 'districts', 'goal', 'answer_count_goal'
        )
        read_only_fields = ('owner', 'questions')

    def to_representation(self, instance: Interview):
        representation = super().to_representation(instance)
        representation['districts'] = [{'id': district.id, 'name': district.name} for district in instance.districts.all()]
        return representation

    # TODO - add validation after interview panel UI is ready