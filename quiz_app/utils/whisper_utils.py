import os
import yt_dlp
import whisper
import time

from django.conf import settings

def download_audio(video_url: str, output_dir: str) -> str:
    """
    Download audio from YouTube video using yt-dlp
    The Audio file is saved temporarily in the specified output path.
    Returns the path to the downloaded audio file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        return os.path.join(output_dir, f"{info['id']}.m4a")


def whisper_transcribe(video_url: str, model_size: str = "base") -> str:
    """
    Calls the download_audio function to download the audio.
    Whisper then transcribes the audio file into text.
    Return the Transcript as text.
    """
    audio_file = download_audio(video_url, settings.TMP_AUDIO_DIR)
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_file)
    transcript = result["text"]

    transcript_file = os.path.join(settings.TMP_TRANSCRIPTS_DIR, f"transcript_{int(time.time())}.txt")
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(transcript)
    
    if os.path.exists(audio_file):
        os.remove(audio_file)

    return transcript, transcript_file