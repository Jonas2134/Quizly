from rest_framework.permissions import BasePermission


class IsUserQuizCreatorPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            quiz = view.get_object()
            return request.user.id == quiz.quiz_creator_id
        return True
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
