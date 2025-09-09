import pytest

from quiz_app.api.serializers import CreateQuizSerializer, QuizSerializer, UpdatedQuizSerializer
from quiz_app.models import Quiz


def test_create_quiz_serializer_creates_instance(db, user, sample_quiz_data):
    data = sample_quiz_data.copy()
    data['url'] = data.get('video_url')
    serializer = CreateQuizSerializer(data=data, context={'user': user})
    assert serializer.is_valid(raise_exception=True) is True
    instance = serializer.save()
    assert isinstance(instance, Quiz)
    assert instance.video_url == sample_quiz_data['video_url']
    assert (instance.title == sample_quiz_data['title']) or (instance.title is None)


def test_quiz_serializer_outputs_expected_fields(db, user, create_quiz):
    quiz = create_quiz(user, title='Serializer Quiz', video_url='http://serializer/')
    serializer = QuizSerializer(quiz)
    data = serializer.data
    assert data.get('title') == quiz.title
    assert data.get('video_url') == quiz.video_url
    assert data.get('id') == quiz.id


def test_updated_quiz_serializer_updates_instance(db, user, create_quiz):
    quiz = create_quiz(user, title='Old Title')
    data = {'title': 'New Title'}
    serializer = UpdatedQuizSerializer(instance=quiz, data=data, partial=True)
    assert serializer.is_valid(raise_exception=True) is True
    updated = serializer.save()
    quiz.refresh_from_db()
    assert quiz.title == 'New Title'
    assert updated.pk == quiz.pk
