import os
import json
import re
import time

from google import genai
from django.conf import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def parse_genai_json(text_output:str):
    cleaned = re.sub(r"^```json\s*|```$", "", text_output.strip())
    return json.loads(cleaned)


def generate_questions(transcript: str, transcript_file: str) -> dict:
    """
    Generate 10 multiple-choice questions using Google GenAI.
    """
    prompt = f"""
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }},
    ...
    (exactly 10 questions)
  ]
}}

Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.

Transcript:
{transcript}
    """

    prompt_file = os.path.join(settings.TMP_PROMPT_DIR, f"prompt_{int(time.time())}.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    text_output = response.text
    quiz_data = parse_genai_json(text_output)

    if os.path.exists(transcript_file) and os.path.exists(prompt_file):
        os.remove(transcript_file)
        os.remove(prompt_file)

    return quiz_data
