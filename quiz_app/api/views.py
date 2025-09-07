from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import CreateQuizSerializer, QuizSerializer
from quiz_app.tasks import process_video


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
