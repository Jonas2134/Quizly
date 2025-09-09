import pytest
from unittest.mock import Mock
from rest_framework.test import force_authenticate

from quiz_app.api.views import CreateQuizView, QuizListView, QuizReviewPutPatchDeleteView


def test_create_list_patch_delete_integration(api_rf, user, sample_quiz_data, monkeypatch):
    mock_generate = Mock()
    mock_update = Mock()
    monkeypatch.setattr('quiz_app.api.views.generate_quiz', mock_generate)
    monkeypatch.setattr('quiz_app.api.views.update_generated_quiz', mock_update)

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

    monkeypatch.setattr('quiz_app.api.views.UpdatedQuizSerializer', FakeUpdatedSerializer)

    payload = sample_quiz_data.copy()
    payload['url'] = payload.get('video_url')

    req = api_rf.post('/api/quizzes/', payload, format='json')
    force_authenticate(req, user=user)
    resp = CreateQuizView.as_view()(req)
    assert resp.status_code == 201
    quiz_id = resp.data.get('id')
    assert quiz_id is not None
    mock_generate.assert_called_once()

    req_list = api_rf.get('/api/quizzes/')
    force_authenticate(req_list, user=user)
    resp_list = QuizListView.as_view()(req_list)
    assert resp_list.status_code == 200
    ids = {item.get('id') for item in resp_list.data}
    assert quiz_id in ids

    patch_payload = {'video_url': 'http://new-url/', 'url': 'http://new-url/'}
    req_patch = api_rf.patch(f'/api/quizzes/{quiz_id}/', patch_payload, format='json')
    force_authenticate(req_patch, user=user)
    resp_patch = QuizReviewPutPatchDeleteView.as_view()(req_patch, pk=quiz_id)
    assert resp_patch.status_code == 200
    mock_update.assert_called_with(quiz_id)

    req_del = api_rf.delete(f'/api/quizzes/{quiz_id}/')
    force_authenticate(req_del, user=user)
    resp_del = QuizReviewPutPatchDeleteView.as_view()(req_del, pk=quiz_id)
    assert resp_del.status_code == 204
