import os
import yt_dlp
import whisper
import json
import time

from google import genai

from django.conf import settings
from django.core.cache import cache

from .models import Quiz, Question


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def download_audio(video_url: str, output_path: str = "/tmp") -> str:
    """
    Simulate audio download process.
    In production, replace this with actual download logic.
    """
    time.sleep(2)
    return output_path


def whisper_transcribe(video_url: str) -> str:
    """
    Simulate transcription process for a video.
    In production, replace this with Whisper transcription.
    """
    time.sleep(3)
    return f"Transcript of {video_url}"


def generate_questions(transcript: str) -> list:
    """
    Generate 10 sample questions from transcript.
    Each question has a title, options, and correct answer.
    """
    return [
        {
            "question_title": f"Question about '{transcript}' #{i+1}",
            "question_options": ["A", "B", "C", "D"],
            "answer": "A"
        }
        for i in range(10)
    ]


def process_video(video_url: str, quiz_title: str, quiz_description: str):
    """
    1. Check if transcript is already cached
    2. If not, transcribe video with Whisper and cache it
    3. Generate questions using the transcript
    4. Save Quiz and Questions to the database
    """
    transcript = cache.get(video_url)
    if not transcript:
        transcript = whisper_transcribe(video_url)
        cache.set(video_url, transcript, timeout=3600)

    questions_data = generate_questions(transcript)

    quiz = Quiz.objects.create(
        title=quiz_title,
        description=quiz_description,
        video_url=video_url
    )

    for q in questions_data:
        question = Question.objects.create(
            question_title=q['question_title'],
            question_options=q['question_options'],
            answer=q['answer']
        )
        quiz.questions.add(question)

    return quiz.id
