from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']

class QuestionForm(forms.Form):
    question = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Ask a question about your resume...',
            'class': 'form-control',
            'rows': 2,
            'style': 'resize:vertical; min-height:38px; max-height:200px;'
        }),
        required=True
    )
