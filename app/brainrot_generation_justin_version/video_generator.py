import random
import os
import io
import subprocess

from gtts import gTTS
import moviepy as mpe
from pydub import AudioSegment
import tempfile


def get_video(snippets):
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(repo_dir, "videos")

    videos_filenames = [f for f in os.listdir(videos_dir) if os.path.isfile(os.path.join(videos_dir, f))]
    if not videos_filenames:
        raise FileNotFoundError("No video files found in the directory.")

    random_video_filename = random.choice(videos_filenames)
    video_path = os.path.join(videos_dir, random_video_filename)

    if os.path.getsize(video_path) == 0:
        raise ValueError(f"Selected video file {random_video_filename} is empty or corrupted.")

    # # Generate TTS in-memory
    # mytext = 'hey penis head this is a voice over long enough that we have an idea of what this stupid fucking voice sounds like.'
    # myobj = gTTS(text=mytext, lang='en', slow=False)
    #
    # mp3_buffer = io.BytesIO()
    # myobj.write_to_fp(mp3_buffer)
    # mp3_buffer.seek(0)
    #
    # # Convert MP3 buffer to WAV (required for moviepy)
    # audio = AudioSegment.from_file(mp3_buffer, format="mp3")
    # wav_buffer = io.BytesIO()
    # audio.export(wav_buffer, format="wav")
    # wav_buffer.seek(0)
    #
    # Load video and add audio
    # my_clip = mpe.VideoFileClip(video_path)
    # audio_background = mpe.AudioFileClip(wav_buffer)
    # final_audio = mpe.CompositeAudioClip([my_clip.audio, audio_background])
    # final_clip = my_clip.set_audio(final_audio)

    # Save to in-memory buffer
    final_clip = mpe.VideoFileClip(video_path)

    # Use a temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as temp_video:
        temp_path = temp_video.name  # Get the file path
        final_clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", threads=4)

        # Read the temp file into BytesIO
        with open(temp_path, "rb") as f:
            video_output = io.BytesIO(f.read())

    return video_output