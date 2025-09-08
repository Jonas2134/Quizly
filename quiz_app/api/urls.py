from django.urls import path

from .views import CreateQuizView, QuizListView, QuizReviewPutPatchDeleteView

urlpatterns = [
    path('createQuiz/', CreateQuizView.as_view(), name='create-quiz'),
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>', QuizReviewPutPatchDeleteView.as_view(), name='quiz-review-put-patch-delete'),
]
