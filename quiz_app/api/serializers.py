from rest_framework import serializers

from quiz_app.models import Quiz, Question


class CreateQuizSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='video_url', required=True)

    class Meta:
        model = Quiz
        fields = ['url']

    def save(self, **kwargs):
        creator = self.context.get('user')
        video_url = self.validated_data.get('video_url')
        save_quiz = Quiz(
            video_url=video_url,
            quiz_creator=creator
        )
        save_quiz.save()
        return save_quiz


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'video_url', 'created_at', 'updated_at', 'questions']


class UpdatedQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'video_url']
