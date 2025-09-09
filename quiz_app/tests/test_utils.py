import os
import json

import pytest
from django.conf import settings

from quiz_app.utils import whisper_utils, genai_utils


def test_download_audio_uses_yt_dlp(monkeypatch, tmp_path):
    class FakeYDL:
        def __init__(self, opts):
            self.opts = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def extract_info(self, video_url, download=True):
            return {'id': 'abc123'}

    monkeypatch.setattr('quiz_app.utils.whisper_utils.yt_dlp.YoutubeDL', FakeYDL)

    out = whisper_utils.download_audio('http://example.com/watch?v=1', str(tmp_path))
    assert out.endswith(os.path.join(str(tmp_path), 'abc123.m4a'))


def test_whisper_transcribe_writes_file_and_cleans_audio(monkeypatch, tmp_path):
    audio_file = tmp_path / 'file.m4a'
    audio_file.write_text('audiobin', encoding='utf-8')

    monkeypatch.setattr('quiz_app.utils.whisper_utils.download_audio', lambda url, out: str(audio_file))

    class FakeModel:
        def transcribe(self, audio_path):
            return {'text': 'transcribed text'}

    monkeypatch.setattr('quiz_app.utils.whisper_utils.whisper.load_model', lambda size: FakeModel())

    monkeypatch.setattr(settings, 'TMP_TRANSCRIPTS_DIR', str(tmp_path))
    monkeypatch.setattr(settings, 'TMP_AUDIO_DIR', str(tmp_path))

    transcript, transcript_file = whisper_utils.whisper_transcribe('http://example.com')
    assert transcript == 'transcribed text'
    assert os.path.exists(transcript_file)
    assert not os.path.exists(str(audio_file))


def test_parse_genai_json_handles_code_fence():
    wrapped = '```json\n{"a": 1, "b": 2}\n```'
    result = genai_utils.parse_genai_json(wrapped)
    assert result == {"a": 1, "b": 2}


def test_generate_questions_calls_genai_and_cleans_files(monkeypatch, tmp_path):
    transcript_file = tmp_path / 'transcript.txt'
    transcript_file.write_text('some transcript')

    monkeypatch.setattr(settings, 'TMP_PROMPT_DIR', str(tmp_path))

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeModels:
        def generate_content(self, model, contents):
            return FakeResponse('```json\n{"title": "T", "description": "D", "questions": []}\n```')

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

    monkeypatch.setattr('quiz_app.utils.genai_utils.client', FakeClient())

    result = genai_utils.generate_questions('transcript text', str(transcript_file))
    assert result['title'] == 'T'
    assert result['description'] == 'D'

    assert not os.path.exists(str(transcript_file))
    prompt_files = list(tmp_path.glob('prompt_*.txt'))
    assert len(prompt_files) == 0
