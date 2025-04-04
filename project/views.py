from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm
from django.contrib import messages
from .forms import ScoreForm
from .models import Project, Notification
from django.http import JsonResponse
from .models import Team
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.db import models


# Create your views here.

@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect("project:project_list")
    else:
        form = ProjectForm()
    return render(request, "create_project.html", {"form": form})


@login_required
def project_list(request):
    projects = Project.objects.all()  # Fetch all projects
    return render(request, "project_list.html", {"projects": projects})

@login_required
def evaluate_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not request.user.is_staff:
        messages.error(request, "Only teachers can evaluate projects.")
        return redirect("project:project_list")

    if request.method == "POST":
        try:
            score = int(request.POST.get('score'))
            if 0 <= score <= 100:
                project.score = score
                project.save()
                messages.success(request, f"✅ Score {score}/100 saved for {project.title}")
            else:
                messages.error(request, "❌ Score must be between 0-100")
        except ValueError:
            messages.error(request, "❌ Invalid score format")

    return redirect("project:project_list")


@login_required
def project_info(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if current user has sent a request for this project
    notification = Notification.objects.filter(
        project=project,
        sender=request.user,  # Check if current user is the sender
        notification_type='join_request'
    ).first()
    
    # Check if project is submitted
    is_submitted = project.is_submitted
    
    return render(request, "project_info.html", {
        "project": project,
        "notification": notification,
        "is_submitted": is_submitted
    })

@login_required
def join_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if project is submitted
    if project.is_submitted:
        messages.error(request, "Cannot join a project that has already been submitted.")
        return redirect("project:project_info", project_id=project.id)
    
    # Check if already requested
    existing_notification = Notification.objects.filter(
        project=project, 
        sender=request.user,  # Check if current user has already sent a request
        notification_type='join_request'
    ).first()
    
    if existing_notification:
        messages.error(request, "⚠️ You have already sent a request to join this project. Please wait for the teacher's response.")
        return redirect("project:project_info", project_id=project.id)
    
    try:
        # Create notification for teacher (project creator)
        Notification.objects.create(
            user=project.created_by,  # Send to project creator (teacher)
            sender=request.user,      # Set the sender as the current user
            project=project,
            message=f"{request.user.username} has requested to join your project '{project.title}'",
            notification_type='join_request',
            status='pending'
        )
        messages.success(request, "✅ Your request to join the project has been sent successfully. The teacher will review it soon.")
    except Exception as e:
        messages.error(request, f"Error sending request: {str(e)}")
    
    return redirect("project:project_info", project_id=project.id)

@login_required
def handle_notification(request, notification_id, action):
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check if user is authorized (must be project creator)
    if request.user != notification.project.created_by:
        messages.error(request, "❌ You are not authorized to perform this action.")
        return redirect("project:project_info", project_id=notification.project.id)
    
    if action == 'accept':
        # Create team if it doesn't exist
        team, created = Team.objects.get_or_create(
            project=notification.project,
            defaults={
                'created_by': notification.project.created_by,
                'status': 'Approved'
            }
        )
        
        # Add student to team
        if notification.sender and notification.sender not in team.members.all():
            team.members.add(notification.sender)
            team.save()
            messages.success(request, f"{notification.sender.get_full_name()} has been added to the team.")
        else:
            messages.warning(request, f"{notification.sender.get_full_name()} is already in the team.")
        
        # Update notification status
        notification.status = 'accepted'
        notification.save()
        
        # Create notification for student
        Notification.objects.create(
            user=notification.sender,
            project=notification.project,
            message=f"Your request to join '{notification.project.title}' has been accepted!",
            notification_type='status_update',
            status='accepted'
        )
        messages.success(request, "Request accepted successfully.")
    else:
        notification.status = 'rejected'
        notification.save()
        
        # Create notification for student
        Notification.objects.create(
            user=notification.sender,
            project=notification.project,
            message=f"Your request to join '{notification.project.title}' has been rejected.",
            notification_type='status_update',
            status='rejected'
        )
        messages.warning(request, "Request rejected.")
    
    return redirect("project:project_info", project_id=notification.project.id)

@login_required
def get_notifications(request):
    # Get notifications for the current user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = {
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'status': n.status,
                'type': n.notification_type,
                'project_id': n.project.id if n.project else None,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_read': n.is_read
            } for n in notifications
        ]
    }
    return JsonResponse(data)


# views.py
@login_required
def create_team(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        # Handle team creation logic
        return redirect('project_detail', project_id=project.id)
    return render(request, 'create_team.html', {'project': project})

@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def collaborate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if project is submitted
    if project.is_submitted:
        messages.error(request, "Cannot collaborate on a project that has already been submitted.")
        return redirect("project:project_info", project_id=project.id)
    
    # Check if user is a team member
    team = Team.objects.filter(project=project).first()
    if not team or request.user not in team.members.all():
        messages.error(request, "You are not authorized to access this page.")
        return redirect("project:project_info", project_id=project.id)
    
    # Get all students (excluding staff and superusers)
    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).exclude(id=request.user.id)  # Exclude current user
    
    # Get team members
    team_members = team.members.all()
    
    # Exclude team members from available students
    if team_members:
        students = students.exclude(id__in=team_members.values_list('id', flat=True))
    
    # Check if all requests are processed
    all_processed = not team or team.status != 'Pending'
    
    context = {
        "project": project,
        "students": students,
        "team": team,
        "team_members": team_members,
        "all_processed": all_processed,
        "is_submitted": project.is_submitted
    }
    
    return render(request, "collaborate.html", context)

@login_required
def send_collaboration_request(request, project_id, student_id):
    project = get_object_or_404(Project, id=project_id)
    student = get_object_or_404(User, id=student_id)
    
    # Check if project is submitted
    if project.is_submitted:
        messages.error(request, "Cannot send collaboration requests for a submitted project.")
        return redirect("project:collaborate", project_id=project.id)
    
    # Get or create team
    team, created = Team.objects.get_or_create(project=project)
    
    # Check if student is already in the team
    if student in team.members.all():
        messages.warning(request, f"{student.username} is already a member of this team.")
        return redirect('project:collaborate', project_id=project.id)
    
    # Add student directly to team
    team.members.add(student)
    messages.success(request, f"{student.username} has been added to the team.")
    
    return redirect('project:collaborate', project_id=project.id)

@login_required
def handle_collaboration_request(request, project_id, student_id, action):
    project = get_object_or_404(Project, id=project_id)
    student = get_object_or_404(User, id=student_id)
    
    # Get team
    team = Team.objects.filter(project=project).first()
    if not team:
        messages.error(request, "Team not found.")
        return redirect("project:collaborate", project_id=project.id)
    
    # Get the collaboration request
    collaboration_request = Notification.objects.filter(
        project=project,
        sender=request.user,
        user=student,
        notification_type='collaboration_request'
    ).first()
    
    if not collaboration_request:
        messages.error(request, "No collaboration request found.")
        return redirect("project:collaborate", project_id=project.id)
    
    if action == 'accept':
        # Add student to team
        if student not in team.members.all():
            team.members.add(student)
            team.save()
            messages.success(request, f"{student.get_full_name()} has been added to the team.")
        else:
            messages.warning(request, f"{student.get_full_name()} is already in the team.")
        
        # Update notification status
        collaboration_request.status = 'accepted'
        collaboration_request.save()
        
        # Create notification for student
        Notification.objects.create(
            user=student,
            project=project,
            message=f"Your request to join '{project.title}' has been accepted!",
            notification_type='status_update',
            status='accepted'
        )
    else:  # reject
        collaboration_request.status = 'rejected'
        collaboration_request.save()
        
        # Create notification for student
        Notification.objects.create(
            user=student,
            project=project,
            message=f"Your request to join '{project.title}' has been rejected.",
            notification_type='status_update',
            status='rejected'
        )
        messages.warning(request, "Request rejected.")
    
    # If the request is AJAX, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Request processed successfully'
        })
    
    return redirect("project:collaborate", project_id=project.id)

@login_required
def your_projects(request):
    # Get all projects where the user is a team member
    user_teams = Team.objects.filter(members=request.user)
    projects = Project.objects.filter(teams__in=user_teams).distinct()
    
    # Create a dictionary to store team status for each project
    project_teams = {project.id: project.teams.filter(members=request.user).first() 
                    for project in projects}
    
    return render(request, "your_projects.html", {
        "projects": projects,
        "project_teams": project_teams
    })

@login_required
def start_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    team = get_object_or_404(Team, project=project)
    
    if team.status == 'Pending':
        messages.error(request, "Cannot start project until all collaboration requests are processed.")
        return redirect("project:collaborate", project_id=project.id)
    
    # Mark project as started
    project.is_started = True
    project.save()
    
    messages.success(request, "Project has been started successfully!")
    return redirect("project:your_projects")

@login_required
def submit_project_file(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if 'project_file' in request.FILES:
            project.file = request.FILES['project_file']
            project.is_submitted = True  # Mark as submitted
            project.save()
            messages.success(request, "File submitted successfully!")
        else:
            messages.error(request, "Please select a file to upload.")
    
    return redirect("project:your_projects")

@login_required
def student_project_list(request):
    # Fetch all projects
    projects = Project.objects.all()
    return render(request, "stud_project_list.html", {"projects": projects}) 

@login_required
def leaderboard(request):
    # Fetch all non-deleted projects, annotate with scores, and sort by score (descending)
    projects = Project.objects.filter(is_deleted=False).order_by('-score', 'title')
    context = {
        "projects": projects,
    }
    return render(request, "leaderboard.html", context)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is a teacher (staff member)
    if not request.user.is_staff:
        messages.error(request, "Only teachers can delete projects.")
        return redirect("project:project_info", project_id=project.id)
    
    # Check if project is submitted
    if not project.is_submitted:
        messages.error(request, "Only submitted projects can be deleted.")
        return redirect("project:project_info", project_id=project.id)
    
    try:
        # Delete the project
        project.delete()
        messages.success(request, "Project deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting project: {str(e)}")
    
    return redirect("project:project_list")