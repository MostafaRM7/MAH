from rest_framework import serializers
from admin_app.models import *
from interview_app.interview_app_serializers.question_serializers import NoGroupQuestionSerializer
from interview_app.models import Interview
from user_app.models import Profile
from user_app.user_app_serializers.resume_serializers import ResumeSerializer


class PricePackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricePack
        fields = ('id', 'name', 'price', 'description', 'created_at')


class InterviewSerializer(serializers.ModelSerializer):
    questions = NoGroupQuestionSerializer(many=True, read_only=True)
    difficulty = serializers.SerializerMethodField(method_name='get_difficulty')
    is_leveled = serializers.SerializerMethodField(method_name='get_is_leveled')

    class Meta:
        model = Interview
        fields = (
            'id', 'name', 'is_active', 'pub_date', 'end_date', 'created_at', 'owner', 'uuid', 'questions',
            'interviewers', 'approval_status', 'price_pack', 'districts',
            'goal_start_date', 'goal_end_date', 'answer_count_goal', 'difficulty', 'is_leveled'
        )
        read_only_fields = ('owner', 'questions')
        ref_name = 'admin_interviews'

    def to_representation(self, instance: Interview):
        representation = super().to_representation(instance)
        representation['districts'] = [{'id': district.id, 'name': district.name} for district in
                                       instance.districts.all()]
        representation['owner'] = {'id': instance.owner.id, 'first_name': instance.owner.first_name,
                                   'last_name': instance.owner.last_name, 'phone_number': instance.owner.phone_number}
        representation['price_pack'] = PricePackSerializer(instance.price_pack).data
        return representation

    def get_is_leveled(self, instance: Interview):
        if instance.questions.count() > 0:
            return not instance.questions.filter(level=0).exists()
        return False

    def get_difficulty(self, instance: Interview):
        if instance.questions.count() > 0 and not instance.questions.filter(level=0).exists():
            try:
                return int(sum(
                    [question.level for question in instance.questions.all()]) / instance.questions.filter(
                    level__gt=0).count())
            except ZeroDivisionError:
                return None
        return None

    def get_interviewers_count(self, instance: Interview):
        return instance.interviewers.count() if instance.interviewers else 0

    def create(self, validated_data):
        districts = validated_data.pop('districts')
        owner = self.context['request'].user.profile
        interview = Interview.objects.create(owner=owner, **validated_data)
        interview.districts.set(districts)
        return interview


class ProfileSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'gender', 'birth_date', 'avatar',
            'address', 'nationality', 'province', 'resume', 'updated_at', 'date_joined', 'ask_for_interview_role',
            'is_interview_role_accepted')
        read_only_fields = ('role', 'updated_at', 'date_joined', 'is_interview_role_accepted')
