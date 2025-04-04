from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # Links project to the teacher who created it
    file = models.FileField(upload_to="project_files/", null=True, blank=True)  # File submission
    score = models.IntegerField(null=True, blank=True)  # Score (only if file is uploaded)
    is_submitted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # New field to track deleted projects
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return self.title
    
class Notification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    TYPE_CHOICES = [
        ('join_request', 'Join Request'),
        ('status_update', 'Status Update'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications',null=True,blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications',null=True,blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notifications',null=True,blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='join_request')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"
    # NOTIFICATION_TYPES = [
    #     ('join_request', 'Join Request'),
    #     ('approval', 'Approval'),
    #     ('rejection', 'Rejection'),
    # ]

    # recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    # sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    # project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="notifications")
    # message = models.TextField()
    # notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    # is_read = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"Notification for {self.recipient.username}: {self.message}"

class Team(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="teams")
    members = models.ManyToManyField(User, related_name="teams")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_teams")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Team for {self.project.title}"
