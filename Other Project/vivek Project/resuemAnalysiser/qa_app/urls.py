from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_resume, name='upload_resume'),
    path('chat/<int:resume_id>/', views.chat, name='chat'),
    path('ask/<int:resume_id>/', views.ask_question, name='ask_question'),
]
