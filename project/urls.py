from django.urls import path
from . import views
from .views import create_project, join_project

app_name = "project"  # Namespace for the app
urlpatterns = [
    path("create/", views.create_project, name="create_project"),  # URL for project creation
    path('list/', views.project_list, name='project_list'),
    path("evaluate/<int:project_id>/", views.evaluate_project, name="evaluate_project"),
    path("student/projects/", views.student_project_list, name="student_projects"),
    path("projects/<int:project_id>/", views.project_info, name="project_info"),
    path("projects/<int:project_id>/join/", views.join_project, name="join_project"),
    path("projects/<int:project_id>/collaborate/", views.collaborate, name="collaborate"),
    path("projects/<int:project_id>/send-request/<int:student_id>/", views.send_collaboration_request, name="send_collaboration_request"),
    path("projects/<int:project_id>/handle-request/<int:student_id>/<str:action>/", views.handle_collaboration_request, name="handle_collaboration_request"),
    path("projects/<int:project_id>/start/", views.start_project, name="start_project"),
    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notification/<int:notification_id>/<str:action>/", views.handle_notification, name="handle_notification"),
    path("notifications/mark-all-read/", views.mark_all_read, name="mark_all_read"),
    path('your-projects/', views.your_projects, name='your_projects'),
    path("projects/<int:project_id>/submit/", views.submit_project_file, name="submit_project_file"),
    path("projects/<int:project_id>/create-team/", views.create_team, name="create_team"),
    path("projects/<int:project_id>/delete/", views.delete_project, name="delete_project"),
]