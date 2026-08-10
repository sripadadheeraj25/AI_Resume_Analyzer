from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Resume, Analysis, SkillMatch
import fitz  # this is PyMuPDF — the package name is fitz even though you pip installed PyMuPDF
from google import genai
import json
import os


# Configure Gemini API using your key from .env
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def home(request):
    # This view just shows the upload form
    # No logic needed here — just render the home template
    return render(request, 'analyzer/home.html')


def extract_text_from_pdf(pdf_file):
    # pdf_file is the uploaded file object Django gives us
    # fitz.open() needs bytes, so we read the file content first
    pdf_bytes = pdf_file.read()

    # Open the PDF from bytes — "pdf" tells fitz the file type
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Loop through every page and extract its text
    text = ""
    for page in doc:
        text += page.get_text()

    return text


def analyze_with_gemini(resume_text, job_description):
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

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )

    # Clean response in case Gemini wraps JSON in ```json ``` markers
    response_text = response.text.strip()
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]

    result = json.loads(response_text.strip())
    return result


def analyze(request):
    print("GEMINI KEY:", os.getenv('GEMINI_API_KEY'))
    # This view only accepts POST requests — form submissions
    # If someone visits /analyze/ directly in browser (GET), send them home
    if request.method != 'POST':
        return redirect('home')

    # Get the uploaded file from the form
    # 'resume_file' must match the name attribute in your HTML form
    resume_file = request.FILES.get('resume_file')

    # Get the job description text from the form
    job_description = request.POST.get('job_description', '').strip()

    # Basic validation — make sure both fields are filled
    if not resume_file:
        messages.error(request, 'Please upload a resume PDF.')
        return redirect('home')

    if not job_description:
        messages.error(request, 'Please paste a job description.')
        return redirect('home')

    # Check file is a PDF
    if not resume_file.name.endswith('.pdf'):
        messages.error(request, 'Only PDF files are supported.')
        return redirect('home')

    # Step 1 — Extract text from the uploaded PDF
    resume_text = extract_text_from_pdf(resume_file)

    if not resume_text.strip():
        messages.error(request, 'Could not extract text from this PDF. Make sure it is not a scanned image.')
        return redirect('home')

    # Step 2 — Save the Resume record to database
    resume = Resume.objects.create(
        file_name=resume_file.name,
        file_url='',  # we will add Supabase upload later
        extracted_text=resume_text
    )

    # Step 3 — Send to Gemini and get analysis
    gemini_result = analyze_with_gemini(resume_text, job_description)

    # Step 4 — Save the Analysis record to database
    analysis = Analysis.objects.create(
        resume=resume,
        job_description=job_description,
        match_score=gemini_result.get('match_score', 0),
        ats_score=gemini_result.get('ats_score', 0),
        feedback=gemini_result.get('feedback', ''),
        suggestions=gemini_result.get('suggestions', '')
    )

    # Step 5 — Save each matched skill
    for skill in gemini_result.get('matched_skills', []):
        SkillMatch.objects.create(
            analysis=analysis,
            skill_name=skill,
            is_matched=True
        )

    # Step 6 — Save each missing skill
    for skill in gemini_result.get('missing_skills', []):
        SkillMatch.objects.create(
            analysis=analysis,
            skill_name=skill,
            is_matched=False
        )

    # Step 7 — Send the analysis to the results template
    return render(request, 'analyzer/result.html', {
        'analysis': analysis,
        'matched_skills': analysis.skills.filter(is_matched=True),
        'missing_skills': analysis.skills.filter(is_matched=False),
    })