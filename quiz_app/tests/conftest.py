import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', email='test@example.com', password='password')


@pytest.fixture
def other_user(db):
    User = get_user_model()
    return User.objects.create_user(username='otheruser', email='other@example.com', password='password')


@pytest.fixture
def sample_quiz_data():
    return {
        'title': 'Sample Quiz',
        'description': 'A test quiz',
        'video_url': 'http://example.com/video',
        'number_of_questions': 3,
    }


@pytest.fixture
def create_quiz(db):
    def _create(user=None, **kwargs):
        from quiz_app.models import Quiz

        defaults = {
            'title': 'Created Quiz',
            'video_url': 'http://example.com/video',
        }
        defaults.update(kwargs)

        UserModel = get_user_model()
        creator_field = None
        for f in Quiz._meta.fields:
            if getattr(f, 'remote_field', None) and getattr(f.remote_field, 'model', None) == UserModel:
                creator_field = f.name
                break

        if creator_field and user is not None:
            defaults[creator_field] = user

        return Quiz.objects.create(**defaults)

    return _create
