from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

from .permissions import IsUserQuizCreatorPermission
from .serializers import CreateQuizSerializer, QuizSerializer, UpdatedQuizSerializer
from quiz_app.tasks import generate_quiz, update_generated_quiz
from quiz_app.models import Quiz


class CreateQuizView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateQuizSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        generate_quiz(instance.id)

        instance.refresh_from_db()

        output_serializer = QuizSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class QuizListView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QuizReviewPutPatchDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsUserQuizCreatorPermission]

    def get_object(self):
        quiz_id = self.kwargs.get('pk')
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
        except Quiz.DoesNotExist:
            raise NotFound('Quiz not found.')
        return quiz

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        quiz = self.get_object()
        serializer = UpdatedQuizSerializer(quiz, data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        update_generated_quiz(quiz.id)

        output_serializer = self.get_serializer(quiz)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
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
        return super().destroy(request, *args, **kwargs)
