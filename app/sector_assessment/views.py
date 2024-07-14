from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, ValidationError

from core.models import Sector, Skill
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from sector_assessment import models
from sector_assessment.serializers import (SectorListSerializer,
                                           SkillListSerializer,
                                           QuestionSerializer,
                                           AssessmentSerializer,
                                           AssessmentRunSerializer,
                                           QuestionAttemptCreateSerializer,
                                           ResultSerializer)
from sector_assessment.utils import create_result


class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


# Should only support GET request
# Only allowed if the user is authenticated
class QuestionView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


# Should only support GET request
# Only allowed if the user is permitted to access
class AssessmentView(viewsets.ReadOnlyModelViewSet):
    # queryset = models.Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request):
        user = request.user

        # Filter the assessments based on allowed_users and start_time
        if not user.is_subscriber:
            raise ValidationError('User is not eligible to take the test')
        try:
            assessment = models.Assessment.objects.filter(
                allowed_users=user,
                # start_time__lte=current_time
            )
        except models.Assessment.DoesNotExist:
            raise NotFound('Assessment not found or access not allowed.')

        serializer = self.get_serializer(assessment, many=True)
        return Response(serializer.data)


class AssessmentRunView(viewsets.ModelViewSet):
    serializer_class = AssessmentRunSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        return serializer.save()

    def list(self, request):
        user = request.user
        assessments = models.AssessmentRun.objects.filter(
            user=user
        )
        serializer = self.get_serializer(assessments, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        assessment_id = request.data.get('assessment')
        if not assessment_id:
            raise ParseError("Could not find Assessment ID")

        if request.data.get('user') != request.user.email:
            raise ValidationError("User requester and attemptor are not same!")
        try:
            assessment = models.Assessment.objects.get(id=assessment_id)
        except models.Assessment.DoesNotExist:
            raise NotFound("Assessment not found.")

        question_attempts_data = request.data.get("question_attempt")
        if not question_attempts_data:
            raise ParseError("No question attempts provided.")

        question_attempts = []
        try:
            for question_attempt in question_attempts_data:
                question_attempt['user'] = request.user.id
                question_serializer = QuestionAttemptCreateSerializer(
                    data=question_attempt
                    )
                question_serializer.is_valid(raise_exception=True)
                question_attempt_object = question_serializer.save()
                question_attempts.append(
                    question_attempt_object
                )
        except ValidationError as e:
            raise ParseError(f"Invalid question attempt data: {e.detail}")

        assessment_run_data = {
            "assessment": assessment.id,
            "user": request.user.id,
            "question_attempt": [question_attempt.id
                                 for question_attempt in question_attempts],
            "question_counter": request.data.get("question_counter"),
            "is_finished": request.data.get("is_finished"),
        }

        try:
            serializer = self.get_serializer(data=assessment_run_data)
            serializer.is_valid(raise_exception=True)
            assessment_run_object = self.perform_create(serializer)
        except ValidationError as e:
            # If assessment run creation fails, delete the
            # created question attempts
            for question_attempt in question_attempts:
                question_attempt.delete()
            raise ParseError(f"Invalid assessment run data: {e.detail}")

        # Return the created instance
        create_result(user, assessment_run_object, question_attempts)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class ResultView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def retrieve(self, request, pk):
        user = request.user
        assessment_run = pk  # request.data.get("assessment_run")
        try:
            result = models.Result.objects.get(
                user=user,
                assessment_run=assessment_run,
            )
        except models.Result.DoesNotExist:
            raise NotFound('Result not found or access not allowed.')

        serializer = self.get_serializer(result)
        return Response(serializer.data)


# class QuestionAttemptView(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]

#     def get_serializer_class(self):
#         if self.action in ('create', 'patch', 'put'):
#             return serializers.QuestionAttemptCreateSerializer
#         return serializers.QuestionAttemptSerializer

#     def create(self, request):
#         """
#         This is to create a new Quesetion attempt
#         """
#         user = request.user
#         user_id = request.data.get("user")
#         choice_id = request.data.get("choice")
#         question_id = request.data.get("question")

#         if not choice_id:
#             raise ParseError("Could not find Selected Choice")
#         if not question_id:
#             raise ParseError("Could not find Question")
#         if user.id != int(user_id):
#            raise ValueError("""User requested for and
#                             user requesting don't match""")

#         question_attempt_data = {
#             "user": user_id,
#             "choice": choice_id,
#             "question": question_id,
#         }

#         serializer = self.get_serializer(data=question_attempt_data)
#         serializer.is_valid(raise_exception=True)

#         self.perform_create(serializer)

#         # Return the created instance
#         headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED,
        #                 headers=headers)

#     @extend_schema(
#     parameters=[
        # OpenApiParameter(name='user', type=int,
        #                  description='ID of the user', required=True),
        # OpenApiParameter(name='question',
        #                  type=int, description='ID of the question',
        #                  required=True),
#     ],
#     responses={200: serializers.QuestionAttemptSerializer}
#     )
#     def retrieve(self, request, *args, **kwargs):
#         """Get choice from the Existing QuestionAttempt"""
#         user = request.user
#         user_id = request.query_params.get("user")
#         question_id = request.query_params.get("question")
#         if not question_id:
#             raise ParseError("Could not find Question")
#         if not user.is_staff:
#             raise ValueError("User is not staff")
        # question_attempt = models.QuestionAttempt.objects.get(user=user_id,
        #                                                       question=question_id)

#         serializer = self.get_serializer(question_attempt)
#         headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_200_OK,
        #                 headers=headers)
