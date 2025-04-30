from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),  # Add this line
    path('syllabus/class/<int:class_id>/', views.syllabus_list, name='syllabus_list'),
    path('syllabus/subject/<int:subject_id>/', views.syllabus_by_subject, name='syllabus_by_subject'),
]
