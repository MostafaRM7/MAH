from rest_framework import serializers
from ..models import *


class OptionSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionSelection
        fields = ('id', 'is_selected')


class DropDownSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropDownSelection
        fields = ('id', 'is_selected')


class TextAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswer
        fields = ('id', 'answer')


class NumberAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberAnswer
        fields = ('id', 'answer')


class IntegerSelectiveAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerSelectiveAnswer
        fields = ('id', 'answer')


class IntegerRangeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerRangeAnswer
        fields = ('id', 'answer')


class PictureFieldAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureAnswer
        fields = ('id', 'answer')


class EmailFieldAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAnswer
        fields = ('id', 'answer')


class LinkAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkAnswer
        fields = ('id', 'answer')


class FileAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAnswer
        fields = ('id', 'answer')
