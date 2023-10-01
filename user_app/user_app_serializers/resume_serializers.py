from rest_framework.serializers import ModelSerializer
from user_app.models import Resume, ResearchHistory, Achievement, Skill, EducationalBackground, WorkBackground


class WorkBackgroundSerializer(ModelSerializer):
    class Meta:
        model = WorkBackground
        fields = ('company', 'position', 'start_date', 'end_date')


class EducationalBackgroundSerializer(ModelSerializer):
    class Meta:
        model = EducationalBackground
        fields = ('degree', 'edu_type', 'field', 'start_date', 'end_date')


class SkillSerializer(ModelSerializer):
    class Meta:
        model = Skill
        fields = ('field', 'level')


class AchievementSerializer(ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('field', 'year')


class ResearchHistorySerializer(ModelSerializer):
    class Meta:
        model = ResearchHistory
        fields = ('field', 'year', 'link')


class ResumeSerializer(ModelSerializer):
    work_backgrounds = WorkBackgroundSerializer(many=True, read_only=True)
    educational_backgrounds = EducationalBackgroundSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    achievements = AchievementSerializer(many=True, read_only=True)
    research_histories = ResearchHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = ('linkedin', 'file', 'work_backgrounds', 'educational_backgrounds', 'skills', 'achievements',
                  'research_histories')
