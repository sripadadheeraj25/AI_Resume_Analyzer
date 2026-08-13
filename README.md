# AI Resume Analyzer

An AI-powered full-stack web application that analyzes resumes against job descriptions and provides instant match scores, skill gap analysis, and improvement suggestions using the Groq LLaMA 3.3 70B language model.

---

## Live Demo

🔗 [Live Demo](https://ai-resume-analyzer-gg43.onrender.com/) &nbsp;&nbsp; | &nbsp;&nbsp; [GitHub](https://github.com/sripadadheeraj25/AI_Resume_Analyzer)

---

## Features

- 📄 **PDF Resume Upload** — Extracts text from uploaded PDF resumes using PyMuPDF
- 🤖 **AI Analysis** — Analyzes resume against job description using Groq LLaMA 3.3 70B
- 📊 **Match Score** — Displays resume-to-job match score with animated Chart.js donut chart
- ✅ **ATS Score** — Checks resume friendliness for Applicant Tracking Systems
- 🟢 **Matched Skills** — Shows skills found in your resume as green pills
- 🔴 **Missing Skills** — Highlights skills missing from your resume as red pills
- 💡 **AI Suggestions** — Provides specific improvement recommendations
- 🕒 **Analysis History** — View and revisit all past analyses
- ☁️ **Cloud Storage** — Resume PDFs stored permanently on Supabase Storage

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 6 |
| Database | PostgreSQL (Supabase) |
| AI Model | Groq API — LLaMA 3.3 70B Versatile |
| PDF Parsing | PyMuPDF (fitz) |
| File Storage | Supabase Storage |
| Frontend | Bootstrap 5.3, Chart.js, Bootstrap Icons (CDN) |
| Deployment | Render (Gunicorn + Whitenoise) |

---

## Project Structure

```
resume_analyzer/
│
├── resume_analyzer/        ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── analyzer/               ← Main app
│   ├── models.py           ← Resume, Analysis, SkillMatch models
│   ├── views.py            ← PDF extraction, Groq AI, DB logic
│   ├── urls.py
│   └── templates/
│       └── analyzer/
│           ├── base.html
│           ├── home.html
│           ├── result.html
│           └── history.html
│
├── static/
├── build.sh                ← Render build script
├── requirements.txt
└── manage.py
```

---

## How It Works

```
User uploads PDF + pastes job description
        ↓
PyMuPDF extracts all text from PDF
        ↓
Text + job description sent to Groq LLaMA 3.3 70B
        ↓
AI returns structured JSON (scores, skills, feedback)
        ↓
Results saved to PostgreSQL (Resume, Analysis, SkillMatch)
        ↓
PDF uploaded to Supabase Storage
        ↓
Results displayed with Chart.js and Bootstrap 5
```

---

## Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/sripadadheeraj/ai-resume-analyzer.git
cd ai-resume-analyzer
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file**
```
SECRET_KEY=your-django-secret-key
DEBUG=True
GROQ_API_KEY=your-groq-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
```

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Start the server**
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local, `False` for production |
| `GROQ_API_KEY` | Groq API key from console.groq.com |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public key |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port (5432) |

---

## Database Models

**Resume** — stores uploaded file info and extracted text

**Analysis** — stores AI results (match score, ATS score, feedback, suggestions)

**SkillMatch** — stores each individual skill as matched or missing

---

## Deployment

Deployed on **Render** with:
- `build.sh` — installs packages, runs collectstatic and migrate
- **Gunicorn** — production WSGI server
- **Whitenoise** — serves static files
- **Supabase PostgreSQL** — cloud database
- **Supabase Storage** — cloud file storage

---

## Author

**Sripada Dheeraj**
- GitHub: [@sripadadheeraj](https://github.com/sripadadheeraj25)
- LinkedIn: [linkedin.com/in/sripadadheeraj](https://linkedin.com/in/sripadadheeraj)
- Email: sripadadheeraj2025@gmail.com
