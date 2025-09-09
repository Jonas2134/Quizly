import pytest
from unittest.mock import Mock
from rest_framework.test import force_authenticate

from quiz_app.models import Quiz
from quiz_app.api.views import (
    CreateQuizView,
    QuizListView,
    QuizReviewPutPatchDeleteView,
)


def test_create_quiz_calls_generate_and_returns_201(api_rf, user, sample_quiz_data, monkeypatch):
    class FakeCreateSerializer:
        def __init__(self, data=None, context=None):
            self.data = data or {}
            self.context = context or {}

        def is_valid(self, raise_exception=False):
            return True

        def save(self):
            creator = self.context.get('user')
            UserModel = type(creator)
            creator_field = None
            for f in Quiz._meta.fields:
                if getattr(f, 'remote_field', None) and getattr(f.remote_field, 'model', None) == UserModel:
                    creator_field = f.name
                    break

            create_kwargs = {'title': self.data.get('title'), 'video_url': self.data.get('video_url')}
            if creator_field:
                create_kwargs[creator_field] = creator

            return Quiz.objects.create(**create_kwargs)

    mock_generate = Mock()
    monkeypatch.setattr('quiz_app.api.views.CreateQuizSerializer', FakeCreateSerializer)
    monkeypatch.setattr('quiz_app.api.views.generate_quiz', mock_generate)

    request = api_rf.post('/api/quizzes/', sample_quiz_data, format='json')
    force_authenticate(request, user=user)
    response = CreateQuizView.as_view()(request)

    assert response.status_code == 201
    assert Quiz.objects.filter(title=sample_quiz_data['title']).exists()
    created = Quiz.objects.get(title=sample_quiz_data['title'])
    mock_generate.assert_called_once_with(created.id)


def test_list_quizzes_returns_200_and_includes_created(api_rf, user, create_quiz):
    q1 = create_quiz(user, title='List Quiz 1')
    q2 = create_quiz(user, title='List Quiz 2')

    request = api_rf.get('/api/quizzes/')
    force_authenticate(request, user=user)
    response = QuizListView.as_view()(request)

    assert response.status_code == 200
    returned_titles = {item.get('title') for item in response.data}
    assert 'List Quiz 1' in returned_titles
    assert 'List Quiz 2' in returned_titles


def test_retrieve_update_partial_delete_work_and_call_update_task(api_rf, user, create_quiz, monkeypatch):
    quiz = create_quiz(user, title='To Be Updated', video_url='http://old-url/')

    class FakeUpdatedSerializer:
        def __init__(self, instance=None, data=None, partial=False):
            self.instance = instance
            self.data = data or {}
            self.partial = partial

        def is_valid(self, raise_exception=False):
            return True

        def save(self):
            for k, v in self.data.items():
                setattr(self.instance, k, v)
            self.instance.save()
            return self.instance

    mock_update_task = Mock()
    monkeypatch.setattr('quiz_app.api.views.UpdatedQuizSerializer', FakeUpdatedSerializer)
    monkeypatch.setattr('quiz_app.api.views.update_generated_quiz', mock_update_task)

    req_get = api_rf.get(f'/api/quizzes/{quiz.id}/')
    force_authenticate(req_get, user=user)
    resp_get = QuizReviewPutPatchDeleteView.as_view()(req_get, pk=quiz.id)
    assert resp_get.status_code == 200

    update_data = {'title': 'Updated Title'}
    req_put = api_rf.put(f'/api/quizzes/{quiz.id}/', update_data, format='json')
    force_authenticate(req_put, user=user)
    resp_put = QuizReviewPutPatchDeleteView.as_view()(req_put, pk=quiz.id)
    assert resp_put.status_code == 200
    mock_update_task.assert_called_with(quiz.id)

    patch_data = {'video_url': 'http://new-url/'}
    req_patch = api_rf.patch(f'/api/quizzes/{quiz.id}/', patch_data, format='json')
    force_authenticate(req_patch, user=user)
    resp_patch = QuizReviewPutPatchDeleteView.as_view()(req_patch, pk=quiz.id)
    assert resp_patch.status_code == 200
    mock_update_task.assert_called_with(quiz.id)

    req_del = api_rf.delete(f'/api/quizzes/{quiz.id}/')
    force_authenticate(req_del, user=user)
    resp_del = QuizReviewPutPatchDeleteView.as_view()(req_del, pk=quiz.id)
    assert resp_del.status_code == 204
    assert not Quiz.objects.filter(pk=quiz.id).exists()
