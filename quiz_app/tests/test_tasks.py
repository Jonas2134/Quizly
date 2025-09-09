import pytest

from quiz_app.tasks import generate_quiz, update_generated_quiz


def test_generate_quiz_creates_questions_and_sets_title_description(db, create_quiz, user, monkeypatch):
    quiz = create_quiz(user, title=None, video_url='http://video/')

    mock_transcript = 'transcribed text'
    mock_transcript_file = 'transcript.srt'
    monkeypatch.setattr('quiz_app.tasks.whisper_transcribe', lambda url: (mock_transcript, mock_transcript_file))

    gen_output = {
        'title': 'Generated Quiz Title',
        'description': 'Generated description',
        'questions': [
            {'question_title': 'Q1', 'question_options': ['a', 'b', 'c'], 'answer': 'a'},
            {'question_title': 'Q2', 'question_options': ['x', 'y', 'z'], 'answer': 'y'},
        ],
    }
    monkeypatch.setattr('quiz_app.tasks.generate_questions', lambda transcript, tf: gen_output)

    returned_id = generate_quiz(quiz.id)

    from quiz_app.models import Quiz, Question

    quiz.refresh_from_db()
    assert returned_id == quiz.id
    assert quiz.title == gen_output['title']
    assert quiz.description == gen_output['description']

    questions = list(Question.objects.filter(quiz=quiz))
    assert len(questions) == 2
    titles = {q.question_title for q in questions}
    assert 'Q1' in titles and 'Q2' in titles


def test_update_generated_quiz_replaces_questions(db, create_quiz, user, monkeypatch):
    quiz = create_quiz(user, title='Initial', video_url='http://video/')
    from quiz_app.models import Question

    Question.objects.create(quiz=quiz, question_title='Old', question_options=['o'], answer='o')
    assert Question.objects.filter(quiz=quiz).count() == 1

    monkeypatch.setattr('quiz_app.tasks.whisper_transcribe', lambda url: ('t', 'f'))
    new_output = {
        'questions': [
            {'question_title': 'New1', 'question_options': ['n1'], 'answer': 'n1'},
        ]
    }
    monkeypatch.setattr('quiz_app.tasks.generate_questions', lambda transcript, tf: new_output)

    returned = update_generated_quiz(quiz.id)
    assert returned == quiz.id

    qs = list(Question.objects.filter(quiz=quiz))
    assert len(qs) == 1
    assert qs[0].question_title == 'New1'
