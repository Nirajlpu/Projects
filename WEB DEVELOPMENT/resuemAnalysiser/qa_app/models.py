
from django.db import models



class JobDescription(models.Model):
	title = models.CharField(max_length=255)
	file = models.FileField(upload_to='jds/', blank=True, null=True)
	text_content = models.TextField(blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

class Resume(models.Model):
	candidate_name = models.CharField(max_length=255, blank=True, null=True)
	file = models.FileField(upload_to='resumes/')
	uploaded_at = models.DateTimeField(auto_now_add=True)
	text_content = models.TextField(blank=True)

	def __str__(self):
		return self.candidate_name or self.file.name.split('/')[-1]
