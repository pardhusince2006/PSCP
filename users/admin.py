from django.contrib import admin
from .models import StudentProfile, TeacherProfile

# Register your models here.

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'student_id', 'department', 'year_of_study')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'faculty_id', 'department', 'designation')
