
# TalentGem: AI-Powered Resume & JD Q&A Platform

TalentGem is a Django-based web application that leverages Google Gemini AI to provide interactive Q&A on candidate resumes and job descriptions, with advanced HR and analytics features.


## Features
- Upload PDF resumes and job descriptions (JD)
- Bulk upload resumes for efficient processing
- Extracts and stores text from PDFs
- AI-powered chat interface for both individual and group Q&A
- Best-fit candidate matching based on JD and resume semantic similarity
- Smart interview question generation with one click
- Chat history management and session-based storage
- Group chat for HR to interact with multiple candidates at once
- Modern Bootstrap 5 UI
- HR analytics and candidate comparison


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
- Answers are generated using both resume and JD context when available
- Handles PDF errors, empty questions, and session management

## Example Use Cases
- Screen and compare candidates against a job description
- Generate tailored interview questions for each candidate
- Enable HR teams to chat with multiple candidates and analyze fit

