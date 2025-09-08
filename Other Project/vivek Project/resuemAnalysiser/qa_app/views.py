

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from .models import Resume
from .forms import ResumeUploadForm, QuestionForm
from .qa_engine import extract_text_from_pdf, split_into_chunks, embed_texts, retrieve_chunks
from .gemini_api import ask_gemini
import os

def upload_resume(request):
	if request.method == 'POST':
		form = ResumeUploadForm(request.POST, request.FILES)
		if form.is_valid():
			resume = form.save(commit=False)
			try:
				text = extract_text_from_pdf(request.FILES['file'])
				if not text.strip():
					messages.error(request, 'No text found in PDF.')
					return render(request, 'qa_app/upload.html', {'form': form})
				resume.text_content = text
				resume.save()
				return redirect('chat', resume_id=resume.id)
			except Exception as e:
				messages.error(request, f'Error processing PDF: {e}')
		else:
			messages.error(request, 'Invalid form submission.')
	else:
		form = ResumeUploadForm()
	return render(request, 'qa_app/upload.html', {'form': form})

def chat(request, resume_id):
	resume = get_object_or_404(Resume, id=resume_id)
	form = QuestionForm()
	chat_history = request.session.get(f'chat_{resume_id}', [])
	return render(request, 'qa_app/chat.html', {
		'resume': resume,
		'form': form,
		'chat_history': chat_history,
	})

def ask_question(request, resume_id):
	resume = get_object_or_404(Resume, id=resume_id)
	if request.method == 'POST':
		form = QuestionForm(request.POST)
		if form.is_valid():
			question = form.cleaned_data['question'].strip()
			if not question:
				if request.headers.get('x-requested-with') == 'XMLHttpRequest':
					return JsonResponse({'success': False, 'error': 'Please enter a question.'})
				messages.error(request, 'Please enter a question.')
				return redirect('chat', resume_id=resume_id)
			chunks = split_into_chunks(resume.text_content)
			chunk_embs = embed_texts(chunks)
			top_chunks = retrieve_chunks(question, chunks, chunk_embs, top_k=3)
			context = '\n'.join(top_chunks)
			try:
				answer = ask_gemini(context, question)
			except Exception as e:
				answer = f"[Error from Gemini: {e}]"
			chat_key = f'chat_{resume_id}'
			chat_history = request.session.get(chat_key, [])
			chat_history.append({'question': question, 'answer': answer})
			request.session[chat_key] = chat_history
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'success': True, 'question': question, 'answer': answer})
			return redirect('chat', resume_id=resume_id)
		else:
			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'success': False, 'error': 'Invalid question.'})
			messages.error(request, 'Invalid question.')
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return JsonResponse({'success': False, 'error': 'Invalid request.'})
	return redirect('chat', resume_id=resume_id)
