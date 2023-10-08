from interview_app.models import Interview
from question_app.question_app_serializers.question_serializers import NoGroupQuestionSerializer
from rest_framework import serializers


class InterviewSerializer(serializers.ModelSerializer):
    questions = NoGroupQuestionSerializer(many=True, read_only=True)
    difficulty = serializers.SerializerMethodField(method_name='get_difficulty')

    class Meta:
        model = Interview
        # TODO - check required fields after UI is ready
        fields = (
            'id', 'name', 'is_active', 'pub_date', 'end_date', 'created_at', 'owner', 'uuid', 'questions',
            'pay_per_answer', 'interviewers', 'approval_status',
            'add_to_approve_queue', 'districts', 'goal', 'answer_count_goal', 'difficulty'
        )
        read_only_fields = ('owner', 'questions')

    def to_representation(self, instance: Interview):
        representation = super().to_representation(instance)
        representation['districts'] = [{'id': district.id, 'name': district.name} for district in
                                       instance.districts.all()]
        representation['interviewers'] = [
            {'id': interviewer.id, 'first_name': interviewer.first_name, 'last_name': interviewer.last_name,
             'phone_number': interviewer.phone_number} for interviewer in
            instance.interviewers.all()]
        return representation

    # TODO - add validation after interview panel UI is ready
    # def validate(self, attrs):
    #     return attrs

    def get_difficulty(self, instance: Interview):
        try:
            return sum(
                [question.difficulty for question in instance.questions.all()]) / instance.questions.count() * 100
        except ZeroDivisionError:
            return 0

    def create(self, validated_data):
        districts = validated_data.pop('districts')
        interviewers = validated_data.pop('interviewers')
        owner = self.context['request'].user.profile
        interview = Interview.objects.create(owner=owner, **validated_data)
        interview.districts.set(districts)
        interview.interviewers.set(interviewers)
        return interview
