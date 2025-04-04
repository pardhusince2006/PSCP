from django.urls import path
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/',views.signup_view, name='signup'),
    path('dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]