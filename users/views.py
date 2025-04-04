from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from django.contrib import messages
from django import forms
from django.http import HttpResponse
from .models import StudentProfile, TeacherProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import get_messages
from project.models import Project





@login_required
def student_dashboard(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    leaderboard_projects = Project.objects.order_by('-score', 'title') 
    return render(request, 'dashboard/student_dashboard.html', {'student': student_profile,"leaderboard_projects": leaderboard_projects})

@login_required
def teacher_dashboard(request):
    teacher_profile = TeacherProfile.objects.get(user=request.user)
    leaderboard_projects = Project.objects.order_by('-score', 'title')
    return render(request, 'dashboard/teacher_dashboard.html', {'teacher': teacher_profile,"leaderboard_projects": leaderboard_projects})

@login_required
def redirect_dashboard(request):
    if hasattr(request.user, 'studentprofile'):
        return redirect('student_dashboard')
    elif hasattr(request.user, 'teacherprofile'):
        return redirect('teacher_dashboard')
    else:
        return redirect('admin:index')



class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('redirect_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# def teacher_dashboard(request):

#     return render(request, 'Home.html')

# def student_dashboard(request):
#     return render(request, 'Home.html')


def signup_view(request):
    if request.method == "POST":
        role = request.POST["role"]
        username = (
            request.POST.get("student-username")
            if role == "student"
            else request.POST.get("teacher-username")
        )
        password = (
            request.POST.get("student-password")
            if role == "student"
            else request.POST.get("teacher-password")
        )
        confirm_password = (
            request.POST.get("student-confirmpassword")
            if role == "student"
            else request.POST.get("teacher-confirmpassword")
        )

        # Password check
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "signup.html")

        # Create User
        user = User.objects.create_user(username=username, password=password)

        if role == "teacher":
            user.is_staff = True  # Mark teacher as staff
            user.save()

        # Create student or teacher profile
        if role == "student":
            StudentProfile.objects.create(
                user=user,
                full_name=request.POST["student_name"],
                email=request.POST["student_email"],
                student_id=request.POST["student_roll"],
                department=request.POST["student_dept"],
                year_of_study=request.POST["student_year"],
            )
        elif role == "teacher":
            TeacherProfile.objects.create(
                user=user,
                full_name=request.POST["teacher_name"],
                faculty_id=request.POST["teacher_id"],
                department=request.POST["teacher_dept"],
                designation=request.POST["teacher_designation"],
            )

        messages.success(request, "Signup successful!")
        return redirect(reverse("login"))

    return render(request, "signup.html")





def some_view(request):
    storage = get_messages(request)
    for message in storage:
        if 'login' in message.tags:
            # Do something with login-related messages
            pass
