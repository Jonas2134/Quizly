from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from .permissions import IsUserQuizCreatorPermission
from .serializers import CreateQuizSerializer, QuizSerializer, UpdatedQuizSerializer
from quiz_app.tasks import generate_quiz, update_generated_quiz
from quiz_app.models import Quiz


class CreateQuizView(generics.CreateAPIView):
    """
    API view for creating a new quiz.
    Only authenticated users can access this endpoint.
    Uses the CreateQuizSerializer to validate and create a new quiz.

    Attributes:
        permission_classes (list): The permission classes to apply to this view.
    """
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Handle POST requests for creating a new quiz.

        1. Validate the incoming data using the serializer.
        2. If valid, save the new quiz, trigger quiz generation, and return the quiz data with HTTP 201 status.
        3. If invalid, return the serializer errors with HTTP 400 status.
        """
        serializer = CreateQuizSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        generate_quiz(instance.id)
        instance.refresh_from_db()
        output_serializer = QuizSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class QuizListView(generics.ListAPIView):
    """
    API view for listing all quizzes.
    Only authenticated users can access this endpoint.
    Uses the QuizSerializer to serialize the quiz data.

    Attributes:
        queryset (QuerySet): The queryset of quizzes to be listed.
        serializer_class (QuizSerializer): The serializer class to use for this view.
        permission_classes (list): The permission classes to apply to this view.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to list all quizzes.

        1. Retrieve all quizzes from the database.
        2. Serialize the quiz data.
        3. Return the serialized data with HTTP 200 status.
        """
        return super().get(request, *args, **kwargs)


class QuizReviewPutPatchDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific quiz.
    Only the quiz creator can update or delete the quiz.
    Uses the QuizSerializer to serialize the quiz data.

    Attributes:
        queryset (QuerySet): The queryset of quizzes to be accessed.
        serializer_class (QuizSerializer): The serializer class to use for this view.
        permission_classes (list): The permission classes to apply to this view.
    """
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsUserQuizCreatorPermission]

    def get_object(self):
        """
        Retrieve the quiz object based on the provided primary key (pk).
        Raises NotFound if the quiz does not exist.

        Returns:
            Quiz: The quiz object if found.
        """
        quiz_id = self.kwargs.get('pk')
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
        except Quiz.DoesNotExist:
            raise NotFound('Quiz not found.')
        return quiz

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve a specific quiz.

        1. Retrieve the quiz object using the provided primary key (pk).
        2. Serialize the quiz data.
        3. Return the serialized data with HTTP 200 status.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Handle PUT requests to update a specific quiz.

        1. Retrieve the quiz object using the provided primary key (pk).
        2. Validate and update the quiz data.
        3. Return the updated quiz data with HTTP 200 status.
        """
        quiz = self.get_object()
        serializer = UpdatedQuizSerializer(quiz, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        update_generated_quiz(quiz.id)
        output_serializer = self.get_serializer(quiz)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests to partially update a specific quiz.

        1. Retrieve the quiz object using the provided primary key (pk).
        2. Validate and partially update the quiz data.
        3. If the video URL is changed, trigger quiz regeneration.
        4. Return the updated quiz data with HTTP 200 status.
        """
        quiz = self.get_object()
        old_url = quiz.video_url
        serializer = UpdatedQuizSerializer(quiz, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if "video_url" in request.data:
            new_url = request.data["video_url"]
            if new_url == old_url or new_url != old_url:
                update_generated_quiz(quiz.id)
        output_serializer = self.get_serializer(quiz)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE requests to delete a specific quiz.

        1. Retrieve the quiz object using the provided primary key (pk).
        2. Delete the quiz object from the database.
        3. Return a success message with HTTP 204 status.
        """
        return super().destroy(request, *args, **kwargs)
