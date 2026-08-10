from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Resume, Analysis, SkillMatch
from groq import Groq
import fitz  # PyMuPDF
import json
import os


# Initialize Groq client using key from .env
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))


def home(request):
    # Simply renders the upload form
    # No logic needed — just show the home page
    return render(request, 'analyzer/home.html')


def extract_text_from_pdf(pdf_file):
    # Read the uploaded file into bytes
    # Django gives us the file in memory, not saved to disk yet
    pdf_bytes = pdf_file.read()

    # Open the PDF from bytes using PyMuPDF
    # stream= means open from memory, filetype= tells fitz it's a PDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Loop through every page and collect all text
    text = ""
    for page in doc:
        text += page.get_text()

    return text


def analyze_with_groq(resume_text, job_description):
    # Build the prompt — instructions we send to the AI
    # We tell it exactly what JSON format to return so we can parse it reliably
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and resume analyzer.

    Analyze the following resume against the job description and return a JSON response.

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}

    Return ONLY a valid JSON object with exactly this structure, no extra text:
    {{
        "match_score": <integer 0-100>,
        "ats_score": <integer 0-100>,
        "matched_skills": [<list of skill strings found in resume>],
        "missing_skills": [<list of skill strings missing from resume>],
        "feedback": "<overall feedback paragraph>",
        "suggestions": "<specific improvement suggestions paragraph>"
    }}
    """

    # Send the prompt to Groq
    # messages= takes a list — system sets AI behavior, user is our actual request
    # temperature=0.3 means low randomness — gives consistent structured output
    response = groq_client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {
                'role': 'system',
                'content': 'You are an expert resume analyzer. Always respond with valid JSON only, no extra text.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        temperature=0.3,
    )

    # Extract the text from Groq's response
    # choices[0] = first (and only) response, .message.content = the actual text
    response_text = response.choices[0].message.content.strip()

    # Clean the response — AI sometimes wraps JSON in ```json ``` markers
    # We strip those out so json.loads() can parse it cleanly
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]

    # Convert JSON string into a Python dictionary
    result = json.loads(response_text.strip())
    return result


def analyze(request):
    # Only accept POST requests — form submissions
    # If someone visits /analyze/ directly in browser (GET request), send them home
    if request.method != 'POST':
        return redirect('home')

    # Get uploaded file from the form
    # request.FILES holds uploaded files, request.POST holds text fields
    resume_file = request.FILES.get('resume_file')
    job_description = request.POST.get('job_description', '').strip()

    # Validate — make sure both fields are filled
    if not resume_file:
        messages.error(request, 'Please upload a resume PDF.')
        return redirect('home')

    if not job_description:
        messages.error(request, 'Please paste a job description.')
        return redirect('home')

    # Validate file type — only accept PDF
    if not resume_file.name.endswith('.pdf'):
        messages.error(request, 'Only PDF files are supported.')
        return redirect('home')

    # Step 1 — Extract text from PDF using PyMuPDF
    resume_text = extract_text_from_pdf(resume_file)

    # If no text was extracted, the PDF is likely a scanned image
    if not resume_text.strip():
        messages.error(request, 'Could not extract text from this PDF. Make sure it is not a scanned image.')
        return redirect('home')

    # Step 2 — Save Resume record to database
    # file_url is empty for now — we will add Supabase storage later
    resume = Resume.objects.create(
        file_name=resume_file.name,
        file_url='',
        extracted_text=resume_text
    )

    # Step 3 — Send resume text and job description to Groq AI
    groq_result = analyze_with_groq(resume_text, job_description)

    # Step 4 — Save Analysis record to database
    # .get() with a default value prevents KeyError if AI misses a field
    analysis = Analysis.objects.create(
        resume=resume,
        job_description=job_description,
        match_score=groq_result.get('match_score', 0),
        ats_score=groq_result.get('ats_score', 0),
        feedback=groq_result.get('feedback', ''),
        suggestions=groq_result.get('suggestions', '')
    )

    # Step 5 — Save each matched skill as a SkillMatch row
    for skill in groq_result.get('matched_skills', []):
        SkillMatch.objects.create(
            analysis=analysis,
            skill_name=skill,
            is_matched=True
        )

    # Step 6 — Save each missing skill as a SkillMatch row
    for skill in groq_result.get('missing_skills', []):
        SkillMatch.objects.create(
            analysis=analysis,
            skill_name=skill,
            is_matched=False
        )

    # Step 7 — Render results page with all data
    # analysis.skills.filter() works because of related_name='skills' in models.py
    return render(request, 'analyzer/result.html', {
        'analysis': analysis,
        'matched_skills': analysis.skills.filter(is_matched=True),
        'missing_skills': analysis.skills.filter(is_matched=False),
    })

def history(request):
    # Fetch all analyses from database, newest first
    # select_related('resume') tells Django to fetch the related Resume row
    # in the same database query instead of making a separate query per row
    # This is called a JOIN — more efficient than N+1 queries
    analyses = Analysis.objects.select_related('resume').order_by('-created_at')

    return render(request, 'analyzer/history.html', {
        'analyses': analyses
    })

def result(request, analysis_id):
    # get_object_or_404 fetches the Analysis with this ID
    # If no analysis exists with that ID, Django automatically returns a 404 page
    # Much cleaner than writing a try/except yourself
    from django.shortcuts import get_object_or_404
    
    analysis = get_object_or_404(Analysis, id=analysis_id)

    return render(request, 'analyzer/result.html', {
        'analysis': analysis,
        'matched_skills': analysis.skills.filter(is_matched=True),
        'missing_skills': analysis.skills.filter(is_matched=False),
    })