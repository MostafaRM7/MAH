from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from user_app.models import Resume, ResearchHistory, Achievement, Skill, EducationalBackground, WorkBackground


class WorkBackgroundSerializer(ModelSerializer):
    class Meta:
        model = WorkBackground
        fields = ('id', 'company', 'position', 'start_date', 'end_date')

    def create(self, validated_data):
        resume_pk = self.context.get('resume_pk')
        return WorkBackground.objects.create(**validated_data, resume_id=resume_pk)


class EducationalBackgroundSerializer(ModelSerializer):
    class Meta:
        model = EducationalBackground
        fields = ('id', 'degree', 'edu_type', 'field', 'start_date', 'end_date', 'university')

    def create(self, validated_data):
        resume_pk = self.context.get('resume_pk')
        return EducationalBackground.objects.create(**validated_data, resume_id=resume_pk)


class SkillSerializer(ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'field', 'level')

    def create(self, validated_data):
        resume_pk = self.context.get('resume_pk')
        return Skill.objects.create(**validated_data, resume_id=resume_pk)


class AchievementSerializer(ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'field', 'year')

    def create(self, validated_data):
        resume_pk = self.context.get('resume_pk')
        return Achievement.objects.create(**validated_data, resume_id=resume_pk)


class ResearchHistorySerializer(ModelSerializer):
    class Meta:
        model = ResearchHistory
        fields = ('id', 'field', 'year', 'link')

    def create(self, validated_data):
        resume_pk = self.context.get('resume_pk')
        return ResearchHistory.objects.create(**validated_data, resume_id=resume_pk)


class ResumeSerializer(ModelSerializer):
    work_backgrounds = WorkBackgroundSerializer(many=True, read_only=True)
    educational_backgrounds = EducationalBackgroundSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    achievements = AchievementSerializer(many=True, read_only=True)
    research_histories = ResearchHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = ('id', 'linkedin', 'file', 'work_backgrounds', 'educational_backgrounds', 'skills', 'achievements',
                  'research_histories')

    def create(self, validated_data):
        user_pk = self.context.get('user_pk')
        return Resume.objects.create(**validated_data, owner_id=user_pk)

    def validate(self, data):
        user_pk = self.context.get('user_pk')
        request = self.context.get('request')
        if Resume.objects.filter(owner_id=user_pk).exists() and request.method in ['POST']:
            raise serializers.ValidationError(
                {'resume': 'شما قبلا رزومه‌ای ثبت کرده‌اید'},
            )
        return data
