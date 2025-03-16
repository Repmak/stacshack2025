import random
import os
from gtts import gTTS
import moviepy as mpe
import io


def get_video(snippets):
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(repo_dir, "videos")
    videos_filenames = [f for f in os.listdir(videos_dir) if os.path.isfile(os.path.join(videos_dir, f))]
    random_video_filename = random.choice(videos_filenames)

    mytext = 'hey penis head this is a voice over long enough that we have an idea of what this stupid fucking voice sounds like.'
    language = 'en'
    myobj = gTTS(text=mytext, lang=language, slow=False)
    myobj.save("typeshit.mp3")

    my_clip = mpe.VideoFileClip(random_video_filename)
    audio_background = mpe.AudioFileClip('typeshit.mp3')
    final_audio = mpe.CompositeAudioClip([my_clip.audio, audio_background])
    final_clip = my_clip.with_audio(final_audio)

    # final_clip.write_videofile("C:/Users/justi/Downloads/output_video.mp4", codec="libx264")

    video_output = io.BytesIO()
    final_clip.write_videofile(video_output, codec="libx264", audio_codec="aac", threads=4)

    video_output.seek(0)

    return video_output