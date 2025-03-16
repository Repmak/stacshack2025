import random
import os
from gtts import gTTS
import moviepy as mpe
import io
from datetime import datetime


def get_video(snippets):
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(repo_dir, "brainrot_generation_justin_version")
    videos_dir = os.path.join(repo_dir, "videos")
    videos_filenames = [f for f in os.listdir(videos_dir) if os.path.isfile(os.path.join(videos_dir, f))]
    random_video_filename = random.choice(videos_filenames)
    print(random_video_filename)

    mytext = 'hey penis head this is a voice over long enough that we have an idea of what this stupid fucking voice sounds like.'
    language = 'en'
    myobj = gTTS(text=mytext, lang=language, slow=False)

    mp3_buffer = io.BytesIO()
    myobj.write_to_fp(mp3_buffer)
    mp3_buffer.seek(0)

    my_clip = mpe.VideoFileClip("/brainrot_generation_justin_version/videos/" + random_video_filename)
    audio_background = mpe.AudioFileClip(mp3_buffer, fps=44100)
    final_audio = mpe.CompositeAudioClip([my_clip.audio, audio_background])
    final_clip = my_clip.with_audio(final_audio)

    # final_clip.write_videofile("C:/Users/justi/Downloads/output_video.mp4", codec="libx264")

    video_output = io.BytesIO()
    final_clip.write_videofile(video_output, codec="libx264", audio_codec="aac", threads=4)

    video_output.seek(0)

    return video_output