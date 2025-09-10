from django.contrib import admin
from django.shortcuts import redirect
from django.contrib import messages

from .models import Quiz
from .tasks import generate_quiz, update_generated_quiz

# Register your models here.

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin interface for the Quiz model.
    Allows admin users to create and update quizzes.
    """
    list_display = ('id', 'title', 'description', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('created_at', 'updated_at')
    fields = ('title', 'description', 'video_url')

    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle quiz generation or updating.
        If the video_url has changed or it's a new quiz, trigger a Function from the tasks.py.
        Uses Django messages to inform the admin user about the status of quiz generation.

        Args:
            request: The current HttpRequest object.
            obj: The Quiz instance being saved.
            form: The form used to create or update the Quiz instance.
            change: A boolean indicating whether the object is being changed (True) or created (False).
        """
        if change:
            old_obj = Quiz.objects.get(pk=obj.pk)
            url_changed = old_obj.video_url != obj.video_url
        else:
            obj.quiz_creator = request.user
            url_changed = True

        super().save_model(request, obj, form, change)

        if url_changed:
            try:
                messages.info(request, "Generating quiz, this may take a moment...")
                if change:
                    quiz_id = update_generated_quiz(obj.id)
                    messages.success(request, f"Quiz (ID: {quiz_id}) updated successfully.")
                else:
                    quiz_id = generate_quiz(obj.id)
                    messages.success(request, f"Quiz (ID: {quiz_id}) generated successfully.")
            except Exception as e:
                messages.error(request, f"Error generating quiz: {str(e)}")
                obj.delete()
