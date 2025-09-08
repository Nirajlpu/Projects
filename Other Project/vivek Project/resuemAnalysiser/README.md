# Resume Q&A System

A Django web app for chat-based Q&A on uploaded PDF resumes using Gemini AI.

## Features
- Upload PDF resume
- Extracts text and stores in DB
- Chat interface: ask questions, get answers from Gemini AI (context-limited)
- Modern Bootstrap 5 UI
- Q&A history per session

## Setup & Run

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Set Gemini API Key:**
   - Create a `.env` file in the project root:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
3. **Migrate DB:**
   ```sh
   python manage.py migrate
   ```
4. **Run server:**
   ```sh
   python manage.py runserver
   ```
5. **Open in browser:**
   - Go to http://127.0.0.1:8000/

## Notes
- Only answers from the uploaded resume content
- Handles PDF errors, empty questions, etc.
- For production, set `DEBUG = False` and configure allowed hosts

