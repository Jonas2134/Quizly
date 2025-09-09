from .models import Quiz, Question
from quiz_app.utils.whisper_utils import whisper_transcribe
from quiz_app.utils.genai_utils import generate_questions


def generate_quiz(quiz_id: int):
    """
    Generate a quiz based on the video URL associated with the given quiz ID.

    Steps:
    1. Load Quiz instance by ID
    2. Transcribe video with Whisper
    3. Generate questions using GenAI
    4. Save Quiz and Questions to the database

    Args:
        quiz_id (int): The ID of the quiz to generate.

    Returns:
        int: The ID of the generated quiz.
    """
    quiz = Quiz.objects.get(id=quiz_id)
    transcript, transcript_file = whisper_transcribe(quiz.video_url)
    quiz_data = generate_questions(transcript, transcript_file)

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


def update_generated_quiz(quiz_id: int):
    """
    Update an existing quiz by regenerating its questions based on the current video URL.

    Steps:
    1. Load Quiz instance by ID
    2. Transcribe video with Whisper
    3. Generate questions using GenAI
    4. Save updated Quiz and Questions to the database

    Args:
        quiz_id (int): The ID of the quiz to update.

    Returns:
        int: The ID of the updated quiz.
    """
    quiz = Quiz.objects.get(id=quiz_id)
    transcript, transcript_file = whisper_transcribe(quiz.video_url)
    quiz_data = generate_questions(transcript, transcript_file)

    quiz.questions.all().delete()

    for q in quiz_data["questions"]:
        Question.objects.create(
            quiz=quiz,
            question_title=q["question_title"],
            question_options=q["question_options"],
            answer=q["answer"],
        )
    return quiz.id
