import json
from django.conf import settings
from google import genai
from google.genai import types


def get_gemini_client():
    """
    Resolve and initialize GenAI client using GEMINI_API_KEY.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        # Fallback to standard environment lookup built into genai.Client()
        return genai.Client()
    return genai.Client(api_key=api_key)


from pydantic import BaseModel, Field
from typing import List


class TimetableExtractionItem(BaseModel):
    day_of_week: str = Field(description="Must be one of: MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY")
    period_number: int = Field(description="Period number starting from 1")
    start_time: str = Field(description="Start time in HH:MM 24-hour format")
    end_time: str = Field(description="End time in HH:MM 24-hour format")
    subject_code: str = Field(description="Subject code (e.g. CS301) or name")
    faculty_email_or_name: str = Field(description="Faculty email or full name")
    room: str = Field(description="Room number or designation")


class TimetableExtractionResult(BaseModel):
    entries: List[TimetableExtractionItem]


def extract_timetable_pdf(file_bytes, file_name="timetable.pdf"):
    """
    Process timetable PDF bytes using gemini-2.5-flash.
    Returns structured data mapping classes and periods.
    """
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type='application/pdf'
                ),
                "Analyze this timetable PDF and extract all weekly timetable entries. For each entry, identify the day, period number, timings, subject code/name, faculty name/email, and room."
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TimetableExtractionResult,
            )
        )
        return response.text
    except Exception as e:
        # Fallback for testing environments
        return json.dumps({"error": str(e), "status": "fallback"})


def extract_calendar_pdf(file_bytes, file_name="calendar.pdf"):
    """
    Process academic calendar PDF bytes using gemini-2.5-flash.
    Returns structured dates and holiday calendars.
    """
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type='application/pdf'
                ),
                "Analyze this academic calendar PDF and return all dates, internal/external exams, holidays, and working days in structured JSON format."
            ]
        )
        return response.text
    except Exception as e:
        return json.dumps({"error": str(e), "status": "fallback"})


def extract_daily_review_topics(review_text, topics_list):
    """
    Determine which topics from the subject topics list are matching the review description.
    """
    try:
        client = get_gemini_client()
        prompt = (
            f"Given the class review text: '{review_text}'\n"
            f"And the list of topics: {json.dumps(topics_list)}\n"
            f"Identify which topics are covered. Return only a JSON array of matching topic titles."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING)
                )
            )
        )
        return json.loads(response.text)
    except Exception:
        # Graceful fallback: return empty list or regex matched topics
        return []
