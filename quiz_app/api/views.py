import django_rq

from django_rq import get_queue
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import CreateQuizSerializer, QuizSerializer
from quiz_app.tasks import process_video




class CreateQuizView(generics.CreateAPIView):
    serializer_class = CreateQuizSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()

        queue = get_queue('default')
        job = queue.enqueue(
            process_video,
            instance.video_url,
            instance.title,
            instance.description
        )
