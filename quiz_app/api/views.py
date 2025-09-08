from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from .permissions import IsUserQuizCreatorPermission
from .serializers import CreateQuizSerializer, QuizSerializer
from quiz_app.tasks import process_video
from quiz_app.models import Quiz


class CreateQuizView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        process_video(instance.id)

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
