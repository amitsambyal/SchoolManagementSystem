from django.urls import path
from .models import SaveExpoTokenView

urlpatterns = [
    path('api/save-expo-token/', SaveExpoTokenView.as_view(), name='save_expo_token'),
]