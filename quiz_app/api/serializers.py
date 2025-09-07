from rest_framework import serializers

from quiz_app.models import Quiz, Question


class CreateQuizSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='video_url', required=True)

    class Meta:
        model = Quiz
        fields = ['url']


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'video_url', 'created_at', 'updated_at', 'questions']
