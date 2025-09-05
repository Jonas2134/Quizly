from django.urls import path, include

urlpatterns = [
    path('', include('auth_app.api.urls')),
    path('', include('quiz_app.api.urls')),
]
