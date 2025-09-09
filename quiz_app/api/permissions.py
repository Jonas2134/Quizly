from rest_framework.permissions import BasePermission


class IsUserQuizCreatorPermission(BasePermission):
    """Custom permission to only allow quiz creators to edit or delete their quizzes."""
    def has_permission(self, request, view):
        """Check if the user is the creator of the quiz for unsafe methods."""
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            quiz = view.get_object()
            return request.user.id == quiz.quiz_creator_id
        return True
    
    def has_object_permission(self, request, view, obj):
        """Delegate to has_permission for object-level checks."""
        return self.has_permission(request, view)
