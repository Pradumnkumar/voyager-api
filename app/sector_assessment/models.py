from django.db import models
from django.utils import timezone

from core.models import User, Skill

import uuid
import os
import datetime
# Create your models here.


def get_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("question_images", filename)


class Question(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='question_created_by',
                                   null=True)
    title = models.CharField(max_length=512)
    question_text = models.TextField(blank=True)
    question_image = models.ImageField(upload_to=get_image_file_path,
                                       blank=True, null=True)

    def __str__(self):
        return self.title


class Choice(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    choice_text = models.CharField(max_length=512, blank=True)
    choice_image = models.ImageField(upload_to=get_image_file_path,
                                     blank=True, null=True)
    question = models.ForeignKey(
        Question,
        related_name='choices',
        on_delete=models.CASCADE
        )
    skills = models.ManyToManyField(Skill)

    class Meta:
        order_with_respect_to = 'question'

    def __str__(self):
        return self.choice_text


class Assessment(models.Model):
    title = models.CharField(max_length=512, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True,
                                   related_name='assessment_created_by')
    questions = models.ManyToManyField(Question)
    max_time = models.DurationField(default=datetime.timedelta(minutes=10))
    max_questions = models.PositiveSmallIntegerField(default=30)
    allowed_users = models.ManyToManyField(User, related_name='allowed_users')

    def __str__(self):
        return self.title


class QuestionAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice,
                               on_delete=models.CASCADE)

    class Meta:
        unique_together = [('user', 'question')]


class AssessmentRun(models.Model):
    assessment = models.ForeignKey(Assessment,
                                   on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True,
                                      auto_now_add=True)
    question_attempt = models.ManyToManyField(QuestionAttempt)
    question_counter = models.PositiveIntegerField(default=timezone.now())
    time_taken = models.DurationField(default=timezone.timedelta(0))
    is_finished = models.BooleanField(default=False)

    class Meta:
        unique_together = ('assessment', 'user',)

    def __str__(self):
        return self.assessment.title


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_score = models.JSONField(default=None)
    sector_score = models.JSONField(default=None)
    assessment_run = models.ForeignKey(AssessmentRun, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('assessment_run', 'user')
