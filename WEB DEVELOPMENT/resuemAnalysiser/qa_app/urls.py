from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.history, name='history'),
    path('resumes/clear/', views.clear_resumes, name='clear_resumes'),
    path('history/clear/', views.clear_history, name='clear_history'),
    path('group-chat/clear/', views.clear_group_chat, name='clear_group_chat'),
    path('group-chat/', views.group_chat, name='group_chat'),
    path('', views.upload_resume, name='upload_resume'),
    path('chat/<int:resume_id>/', views.chat, name='chat'),
    path('ask/<int:resume_id>/', views.ask_question, name='ask_question'),
    path('bulk-upload/', views.bulk_upload_resumes, name='bulk_upload_resumes'),
    path('upload-jd/', views.upload_jd, name='upload_jd'),
    path('bestfit/', views.bestfit_candidates, name='bestfit_candidates'),
    path('reset/', views.reset_system, name='reset_system'),
]
