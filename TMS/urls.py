from django.urls import path
from .views import StudentAutocomplete, driver_tracking_view
from .views import track_bus,update_location_api

urlpatterns = [
    path('student-autocomplete/', StudentAutocomplete.as_view(), name='student-autocomplete'),
    path('track-bus/', track_bus, name='track_bus'),
    path('api/update-location/', update_location_api, name='update_location_api'),
    path('driver/tracking/', driver_tracking_view, name='driver_tracking'),
]