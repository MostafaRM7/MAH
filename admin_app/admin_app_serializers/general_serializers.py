from django.db import transaction
from rest_framework import serializers
from admin_app.models import *
from interview_app.interview_app_serializers.question_serializers import NoGroupQuestionSerializer
from interview_app.models import Interview, Ticket
from user_app.models import Profile
from user_app.user_app_serializers.resume_serializers import ResumeSerializer


class PricePackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricePack
        fields = ('id', 'name', 'price', 'description', 'created_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['interviews'] = [{'id': interview.id, 'name': interview.name} for interview in
                                        instance.interviews.all()]
        return representation


class InterviewSerializer(serializers.ModelSerializer):
    questions = NoGroupQuestionSerializer(many=True, read_only=True)
    difficulty = serializers.SerializerMethodField(method_name='get_difficulty')
    is_leveled = serializers.SerializerMethodField(method_name='get_is_leveled')
    answer_count = serializers.SerializerMethodField(method_name='get_answer_count')

    class Meta:
        model = Interview
        fields = (
            'id', 'name', 'is_active', 'pub_date', 'end_date', 'created_at', 'owner', 'uuid', 'questions',
            'interviewers', 'approval_status', 'price_pack', 'districts', 'answer_count', 'required_interviewer_count',
            'goal_start_date', 'goal_end_date', 'answer_count_goal', 'difficulty', 'is_leveled'
        )
        read_only_fields = ('owner', 'questions', 'approval_status')
        ref_name = 'admin_app_interviews'

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
            if not instance.questions.filter(level=0).exists():
                if instance.approval_status == Interview.PENDING_LEVEL_ADMIN:
                    if instance.price_pack:
                        instance.approval_status = Interview.SEARCHING_FOR_INTERVIEWERS
                        instance.save()
                    else:
                        instance.approval_status = Interview.PENDING_PRICE_ADMIN
                        instance.save()
                return True
            else:
                instance.approval_status = Interview.PENDING_LEVEL_ADMIN
                instance.save()
                return False
        return False

    def get_answer_count(self, instance: Interview):
        return instance.answer_sets.count()

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

    @transaction.atomic
    def create(self, validated_data):
        districts = validated_data.pop('districts')
        owner = self.context['request'].user.profile
        interview = Interview.objects.create(owner=owner, **validated_data)
        interview.districts.set(districts)
        return interview


class ProfileSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer(read_only=True)
    questionnaires_count = serializers.SerializerMethodField(method_name='get_questionnaires_count')

    class Meta:
        model = Profile
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'gender', 'birth_date', 'avatar',
            'address', 'nationality', 'province', 'resume', 'updated_at', 'date_joined', 'ask_for_interview_role',
            'is_interview_role_accepted', 'is_active', 'questionnaires_count')
        read_only_fields = ('role', 'updated_at', 'date_joined', 'is_interview_role_accepted')
        ref_name = 'admin_app_profile'

    def get_questionnaires_count(self, instance: Profile):
        return instance.questionnaires.count()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'text', 'sender', 'receiver', 'is_read', 'sent_at', 'interview')
        read_only_fields = ('sender', 'is_read', 'sent_at')
        ref_name = 'admin_app_ticket'

    def to_representation(self, instance: Ticket):
        representation = super().to_representation(instance)
        if instance.sender == self.context['request'].user.profile:
            representation['sender'] = 'me'
        else:
            representation['sender'] = {
                'id': instance.sender.id,
                'first_name': instance.sender.first_name,
                'last_name': instance.sender.last_name,
                'phone_number': instance.sender.phone_number,
                'email': instance.sender.email,
                'role': instance.sender.role,
                'interview': {
                    'id': instance.interview.id,
                    'uuid': instance.interview.uuid,
                    'name': instance.interview.name
                } if instance.interview else None
            }
        if instance.receiver is None:
            representation['receiver'] = 'admin'
        return representation

    def validate(self, data):
        sender = self.context['request'].user.profile
        if sender == data.get('receiver'):
            raise serializers.ValidationError(
                {'receiver': 'فرستنده و گیرنده نمی توانند یکی باشند'}
            )
        return data

    def create(self, validated_data):
        sender = self.context['request'].user.profile
        ticket = Ticket.objects.create(sender=sender, **validated_data)
        return ticket
