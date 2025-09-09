from rest_framework import serializers

from quiz_app.models import Quiz, Question


class CreateQuizSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new quiz.
    Accepts a video URL and associates the quiz with the creator.

    Fields:
        url (str): The URL of the video for the quiz.
    """
    url = serializers.CharField(source='video_url', required=True)

    class Meta:
        """
        Meta class for CreateQuizSerializer.
        Specifies the model and fields to be used.

        Attributes:
            model (Quiz): The quiz model.
            fields (list): The fields to be included in the serializer.
        """
        model = Quiz
        fields = ['url']

    def save(self, **kwargs):
        """
        Save the quiz instance.
        Associates the quiz with the creator from the context.
        """
        creator = self.context.get('user')
        video_url = self.validated_data.get('video_url')
        save_quiz = Quiz(
            video_url=video_url,
            quiz_creator=creator
        )
        save_quiz.save()
        return save_quiz


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz questions.
    Includes question title, options, answer, and timestamps.

    Fields:
        id (int): The unique identifier of the question.
        question_title (str): The title of the question.
        question_options (list): The options for the question.
        answer (str): The correct answer for the question.
        created_at (datetime): The timestamp when the question was created.
        updated_at (datetime): The timestamp when the question was last updated.
    """
    class Meta:
        """
        Meta class for QuestionSerializer.
        Specifies the model and fields to be used.

        Attributes:
            model (Question): The question model.
            fields (list): The fields to be included in the serializer.
        """
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for quizzes.
    Includes quiz details and associated questions.

    Fields:
        id (int): The unique identifier of the quiz.
        title (str): The title of the quiz.
        description (str): The description of the quiz.
        video_url (str): The URL of the video for the quiz.
        created_at (datetime): The timestamp when the quiz was created.
        updated_at (datetime): The timestamp when the quiz was last updated.
        questions (list): The list of associated questions.
    """
    questions = QuestionSerializer(many=True)

    class Meta:
        """
        Meta class for QuizSerializer.
        Specifies the model and fields to be used.

        Attributes:
            model (Quiz): The quiz model.
            fields (list): The fields to be included in the serializer.
        """
        model = Quiz
        fields = ['id', 'title', 'description', 'video_url', 'created_at', 'updated_at', 'questions']


class UpdatedQuizSerializer(serializers.ModelSerializer):
    """
    Serializer for updating quiz details.
    Allows updating the title, description, and video URL.

    Fields:
        title (str): The title of the quiz.
        description (str): The description of the quiz.
        video_url (str): The URL of the video for the quiz.
    """
    class Meta:
        """
        Meta class for UpdatedQuizSerializer.
        Specifies the model and fields to be used.

        Attributes:
            model (Quiz): The quiz model.
            fields (list): The fields to be included in the serializer.
        """
        model = Quiz
        fields = ['title', 'description', 'video_url']
