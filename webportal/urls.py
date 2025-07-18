from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('syllabus/', views.syllabus, name='syllabus'),
    path('privacy-policy/',views.privacy_policy, name='privacy_policy'),
    path('delete-account-request/',views.delete_account_request,name='delete_account_request'),
    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),  # Add this line
    path('subjects/<int:class_id>/', views.get_subjects_by_class, name='get_subjects_by_class'),
   ]
