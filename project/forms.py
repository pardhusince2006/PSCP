from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "deadline"]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),  # Adds a calendar picker
        }
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['file']

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['score']