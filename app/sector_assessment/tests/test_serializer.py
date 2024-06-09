from sector_assessment.models import (Question,
                                      Choice,
                                      Assessment,
                                      QuestionAttempt)
from sector_assessment.serializers import (QuestionSerializer,
                                           ChoiceSerializer,
                                           AssessmentSerializer,
                                           QuestionAttemptSerializer)

import io

from django.contrib.auth import get_user_model
import create_db as cdb
from sector_assessment.tests import expected_serialized_data

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase

user = get_user_model()


class SerializerTest(APITestCase):
    def setUp(self):
        self.user = user
        cdb.create_super_user()
        cdb.create_staff()
        cdb.create_user()
        cdb.create_sector()
        cdb.create_skill()
        cdb.create_question()
        cdb.create_choice()
        cdb.create_assessment()
        QuestionAttempt.objects.create(
            id=1,
            question=Question.objects.get(id=1),
            choice=Choice.objects.get(id=1),
            user=self.user.objects.all()[1]
        )

    def test_serialize_question_from_model_object(self):
        question = Question.objects.all()[0]
        serializer_data = QuestionSerializer(question)
        data = expected_serialized_data.question
        self.assertEqual(serializer_data.data, data)

    def test_serialize_question_from_json(self):
        question = Question.objects.all()[0]
        serializer = QuestionSerializer(question)
        content = JSONRenderer().render(serializer.data)
        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serializer = QuestionSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())

    def test_serialize_choice_from_model_object(self):
        choice = Choice.objects.all()[0]
        serializer_data = ChoiceSerializer(choice)
        data = expected_serialized_data.choice
        self.assertEqual(serializer_data.data, data)

    def test_serialize_choice_from_json(self):
        choice = Choice.objects.all()[0]
        serializer = ChoiceSerializer(choice)
        content = JSONRenderer().render(serializer.data)
        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serializer = ChoiceSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())

    def test_serialize_assessment_from_model_object(self):
        assessment = Assessment.objects.get(id=1)
        serializer = AssessmentSerializer(assessment)
        data = expected_serialized_data.assessment
        self.assertEqual(data, serializer.data)

    def test_serialize_assessment_from_json(self):
        assessment = Assessment.objects.get(id=1)
        serializer = AssessmentSerializer(assessment)
        content = JSONRenderer().render(serializer.data)
        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serializer = AssessmentSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())

    def test_serialize_question_attempt_from_model_object(self):
        question_attempt = QuestionAttempt.objects.all()[0]
        serializer = QuestionAttemptSerializer(question_attempt)
        # print(serializer.data)
        data = expected_serialized_data.question_attempt
        self.assertEqual(data, serializer.data)

    def test_serialize_question_attemp_from_json(self):
        question_attempt = QuestionAttempt.objects.all()[0]
        serializer = QuestionAttemptSerializer(question_attempt)
        content = JSONRenderer().render(serializer.data)
        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serializer = QuestionAttemptSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())
