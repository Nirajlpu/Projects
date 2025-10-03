
from django.db import models


class Resume(models.Model):
	file = models.FileField(upload_to='resumes/')
	uploaded_at = models.DateTimeField(auto_now_add=True)
	text_content = models.TextField(blank=True)

	def __str__(self):
		return self.file.name.split('/')[-1]
