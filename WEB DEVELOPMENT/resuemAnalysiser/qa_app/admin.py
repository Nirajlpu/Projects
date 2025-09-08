
from django.contrib import admin
from .models import Resume, JobDescription

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
	list_display = ('candidate_name', 'file', 'uploaded_at')

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
	list_display = ('title', 'uploaded_at')
