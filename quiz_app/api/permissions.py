from rest_framework.permissions import BasePermission


class IsUserQuizCreatorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            quiz = view.get_object()
            return request.user == quiz.quiz_creator
        return True
