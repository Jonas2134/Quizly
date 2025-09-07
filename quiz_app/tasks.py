from .models import Quiz, Question
from quiz_app.utils.whisper_utils import whisper_transcribe
from quiz_app.utils.genai_utils import generate_questions


def process_video(quiz_id: int):
    """
    1. Load Quiz instance by ID
    2. Transcribe video with Whisper
    3. Generate questions using GenAI
    4. Save Quiz and Questions to the database
    """
    quiz = Quiz.objects.get(id=quiz_id)
    transcript = whisper_transcribe(quiz.video_url)
    quiz_data = generate_questions(transcript)

    quiz.title = quiz_data["title"]
    quiz.description = quiz_data["description"]
    quiz.save()

    for q in quiz_data["questions"]:
        question = Question.objects.create(
            quiz=quiz,
            question_title=q['question_title'],
            question_options=q['question_options'],
            answer=q['answer']
        )
        quiz.questions.add(question)

    return quiz.id
