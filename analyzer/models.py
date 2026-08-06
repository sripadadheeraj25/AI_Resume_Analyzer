from django.db import models


class Resume(models.Model):
    # The original file name — e.g. "john_resume.pdf"
    file_name = models.CharField(max_length=255)

    # URL to the file stored in Supabase Storage
    file_url = models.URLField(max_length=500)

    # The raw text extracted from the PDF by PyMuPDF
    extracted_text = models.TextField()

    # When was this resume uploaded
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class Analysis(models.Model):
    # Which resume was analyzed — ForeignKey links to Resume table
    # on_delete=CASCADE means if resume is deleted, its analyses are deleted too
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')

    # The job description the user pasted
    job_description = models.TextField()

    # Overall match score from 0 to 100
    match_score = models.IntegerField(default=0)

    # ATS friendliness score from 0 to 100
    ats_score = models.IntegerField(default=0)

    # Full AI feedback stored as text
    feedback = models.TextField(blank=True)

    # Improvement suggestions from Gemini
    suggestions = models.TextField(blank=True)

    # When was this analysis done
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.resume.file_name} - Score: {self.match_score}"


class SkillMatch(models.Model):
    # Which analysis this skill belongs to
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='skills')

    # The skill name — e.g. "Python", "Machine Learning", "Communication"
    skill_name = models.CharField(max_length=100)

    # True = skill was found in resume. False = skill is missing
    is_matched = models.BooleanField(default=False)

    def __str__(self):
        status = "Matched" if self.is_matched else "Missing"
        return f"{self.skill_name} - {status}"