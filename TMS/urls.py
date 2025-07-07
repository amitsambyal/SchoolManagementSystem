from django.urls import path
from .views import StudentAutocomplete

urlpatterns = [
    path('student-autocomplete/', StudentAutocomplete.as_view(), name='student-autocomplete'),
]