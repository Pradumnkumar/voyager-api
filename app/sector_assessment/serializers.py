from core.models import Sector, Skill
from sector_assessment.models import (Question, Choice,
                                      Assessment, QuestionAttempt,
                                      AssessmentRun, Result)
from user.serializers import UserSerializer

from rest_framework import serializers


class SectorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sector
        fields = ['name', 'description']


# Using StringRelatedField for serialization to avoid
# unnecessary data clutter, returns str(Sector)
class SkillListSerializer(serializers.ModelSerializer):
    sectors = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Skill
        fields = ['name', 'sectors']


# Refer to:
# https://www.django-rest-framework.org/api-guide/relations/
# Similar to skill list serializer
class ChoiceSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    skills = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Choice
        fields = ('id', 'choice_text', 'choice_image',
                  'question', 'skills')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = ('id', 'title', 'question_text', 'question_image', 'choices')


class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Assessment
        fields = ('id', 'title', 'questions',
                  'max_time', 'max_questions')


class QuestionAttemptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAttempt
        fields = ('user', 'question', 'choice')


class QuestionAttemptSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    choice = ChoiceSerializer(read_only=True)

    class Meta:
        model = QuestionAttempt
        fields = ('id', 'user', 'question', 'choice')

    def create(self, validated_data):
        user = validated_data.get('user')
        question = validated_data.get('question')
        choice = validated_data.get('choice')
        return QuestionAttempt.objects.create(user=user,
                                              question=question,
                                              choice=choice)


class AssessmentRunSerializer(serializers.ModelSerializer):
    # assessment = AssessmentSerializer(read_only=True)
    # user = UserSerializer(read_only=True)
    # question_attempt = QuestionAttemptSerializer(many=True, read_only=True)
    class Meta:
        model = AssessmentRun
        fields = ('id', 'assessment', 'user', 'question_counter',
                  'question_attempt', 'time_taken', 'is_finished')


class ResultSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    assessment_run = AssessmentRunSerializer(read_only=True)

    class Meta:
        model = Result
        fields = ('id', 'user', 'assessment_run',
                  'sector_score', 'skill_score')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request', None)
        if request and not request.user.is_subscriber:
            representation.pop('sector_score', None)
        return representation
