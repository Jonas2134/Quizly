from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class Quiz(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField()
    quiz_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizes')

    def __str__(self):
        return f"Quiz {self.id}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_title = models.CharField(max_length=200, null=True, blank=True)
    question_options = models.JSONField()
    answer = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
