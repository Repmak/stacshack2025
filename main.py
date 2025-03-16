import sys
import os
import random
import textwrap
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Tuple

import requests
import numpy as np
import cv2
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from gtts import gTTS
import asyncio
import edge_tts

# Function to directly download videos from URLs
def download_file(url, output_path):
    """Download a file from a direct URL."""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return output_path

# Function to get background videos
def get_background_videos(num_videos: int = 3) -> List[str]:
    """Get background videos from local files or download from direct URLs."""
    # Check for local videos first
    print("Looking for local video files...")
    local_videos = []
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        local_videos.extend(list(Path('.').glob(f'*parkour*{ext}')))
        local_videos.extend(list(Path('.').glob(f'*minecraft*{ext}')))

    if local_videos:
        print(f"Found {len(local_videos)} local video files.")
        # Use local videos
        return [str(video) for video in random.sample(local_videos, min(num_videos, len(local_videos)))]

    # If no local videos, use direct URLs instead of YouTube
    # These are direct download URLs for free-to-use Minecraft parkour videos
    print("No local videos found. Downloading videos from direct URLs...")
    direct_urls = [
        "https://cdn.pixabay.com/vimeo/328412699/minecraft-25983.mp4",
        "https://cdn.pixabay.com/vimeo/388774000/minecraft-35287.mp4",
        "https://cdn.pixabay.com/vimeo/414114703/blocks-38287.mp4",
        "https://cdn.pixabay.com/vimeo/431950491/cubes-40342.mp4",
        "https://videos.pexels.com/videos/pixel-game-2499611"
    ]

    # Fallback to generic videos if we can't get Minecraft content
    fallback_urls = [
        "https://cdn.pixabay.com/vimeo/190922894/abstract-10818.mp4",
        "https://cdn.pixabay.com/vimeo/531682200/video-game-86879.mp4",
        "https://cdn.pixabay.com/vimeo/563217483/video-game-92840.mp4",
        "https://cdn.pixabay.com/vimeo/358371580/3d-31720.mp4",
        "https://cdn.pixabay.com/vimeo/190923069/abstract-10819.mp4"
    ]

    # Try to download videos
    temp_dir = tempfile.mkdtemp()
    downloaded_videos = []

    # First try the Minecraft URLs
    for i, url in enumerate(direct_urls):
        if len(downloaded_videos) >= num_videos:
            break

        output_path = os.path.join(temp_dir, f"background_{i}.mp4")
        try:
            print(f"Downloading video {i+1}/{len(direct_urls)}...")
            download_file(url, output_path)
            downloaded_videos.append(output_path)
            print(f"Successfully downloaded: {output_path}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    # If we still need more videos, try the fallback URLs
    if len(downloaded_videos) < num_videos:
        for i, url in enumerate(fallback_urls):
            if len(downloaded_videos) >= num_videos:
                break

            output_path = os.path.join(temp_dir, f"fallback_{i}.mp4")
            try:
                print(f"Downloading fallback video {i+1}/{len(fallback_urls)}...")
                download_file(url, output_path)
                downloaded_videos.append(output_path)
                print(f"Successfully downloaded: {output_path}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")

    # If we still don't have any videos, create a simple video
    if not downloaded_videos:
        print("Failed to download videos. Creating a simple background...")
        output_path = os.path.join(temp_dir, "generated_background.mp4")
        create_simple_background_video(output_path, duration=60)
        downloaded_videos.append(output_path)

    return downloaded_videos

# Function to create a simple background video if all downloads fail
def create_simple_background_video(output_path, width=1280, height=720, duration=60, fps=30):
    """Create a simple animated background video."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Create a simple animated background
    frames = int(duration * fps)
    for i in range(frames):
        # Create a gradient background with moving blocks
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Add a gradient background
        for y in range(height):
            color = int(255 * y / height)
            frame[y, :] = [0, 0, color]  # Blue gradient

        # Add some moving blocks
        time_factor = i / fps
        for j in range(10):
            block_x = int((width * 0.1 * j + time_factor * 100) % width)
            block_y = int((height * 0.5 + 100 * np.sin(time_factor + j * 0.5)) % height)
            block_size = 50 + int(20 * np.sin(time_factor * 2 + j))

            # Ensure block stays in frame
            if block_x + block_size > width:
                block_size = width - block_x
            if block_y + block_size > height:
                block_size = height - block_y

            if block_size > 0:
                color = [(j * 20) % 255, (255 - j * 20) % 255, (127 + j * 10) % 255]
                frame[block_y:block_y+block_size, block_x:block_x+block_size] = color

        out.write(frame)

    out.release()
    return output_path

# Function to process CS lecture content
def process_lecture_content(lecture_text: str) -> List[str]:
    """Process lecture content into brain rot style sentences with smaller chunks."""
    # Split the text into sentences
    sentences = [s.strip() for s in lecture_text.replace('\n', ' ').split('.') if s.strip()]
    
    # Brain rot phrases
    brain_rot_intros = [
        "no way bro...",
        "literally mind blowing...",
        "this is insane...",
        "you won't believe this...",
        "this will change your life...",
        "wait till you see this...",
        "i can't even...",
        "this is crazy fr fr...",
        "watch till the end..."
    ]

    brain_rot_outros = [
        "...and that's crazy",
        "...like fr fr no cap",
        "...mind = blown",
        "...this changed everything",
        "...that's wild",
        "...and nobody is talking about this",
        "...and that's just facts",
        "...I'm literally shook"
    ]
    
    # Process sentences into smaller chunks
    processed_chunks = []
    
    for sentence in sentences:
        # Add brain rot phrases
        if random.random() < 0.3:
            sentence = random.choice(brain_rot_intros) + " " + sentence
        if random.random() < 0.3:
            sentence = sentence + " " + random.choice(brain_rot_outros)
            
        # Split long sentences into smaller chunks (roughly 5-8 words per chunk)
        words = sentence.split()
        if len(words) > 8:
            # Create chunks of 5-8 words
            chunk_size = random.randint(5, 8)
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i+chunk_size])
                # Don't add intro/outro phrases to chunks from the same sentence
                processed_chunks.append(chunk)
        else:
            # Short enough sentence, keep as is
            processed_chunks.append(sentence)
    
    return processed_chunks

# Function to generate TTS audio using Edge TTS
async def generate_tts_audio_edge(sentence: str, output_path: str) -> None:
    """Generate TTS audio using Edge TTS with a more energetic voice."""
    # en-US-AriaNeural is a good energetic female voice
    # en-US-GuyNeural is a good male voice
    voice = "en-US-AriaNeural"
    
    # Increase enthusiasm with higher pitch and faster rate
    communicate = edge_tts.Communicate(sentence, voice)
    # Increase speed and pitch for more enthusiasm
    communicate.rate = "+25%" 
    communicate.pitch = "+15%"
    
    # Add voice style for more enthusiasm
    # Options include: "cheerful", "excited", "friendly", "enthusiastic"
    communicate.style = "cheerful"
    
    await communicate.save(output_path)

def generate_tts_audio(sentences: List[str], output_path: str) -> tuple:
    """Generate text-to-speech audio for each sentence and combine them."""
    temp_dir = tempfile.mkdtemp()
    audio_files = []
    processed_audio_files = []
    segment_durations = []

    # 1. Generate all audio files first
    for i, sentence in enumerate(sentences):
        audio_path = os.path.join(temp_dir, f"audio_{i}.mp3")
        
        try:
            # Run the async function using asyncio
            asyncio.run(generate_tts_audio_edge(sentence, audio_path))
            audio_files.append(audio_path)
        except Exception as e:
            print(f"Error with Edge TTS, falling back to gTTS: {e}")
            tts = gTTS(text=sentence, lang='en', slow=False)
            tts.save(audio_path)
            audio_files.append(audio_path)

    # 2. Process each audio file - but use less aggressive parameters
    for i, audio_file in enumerate(audio_files):
        processed_path = os.path.join(temp_dir, f"processed_{i}.mp3")
        
        # Use gentler silence removal - only trim start/end slightly
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', audio_file,
                '-af', 'silenceremove=start_periods=1:start_threshold=-25dB:start_silence=0.15:detection=peak,'
                       'silenceremove=stop_periods=1:stop_threshold=-25dB:stop_silence=0.15:detection=peak',
                processed_path
            ], check=True)
        except:
            # If ffmpeg fails, use the original file
            processed_path = audio_file
        
        # Get duration
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 
             'default=noprint_wrappers=1:nokey=1', processed_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            duration = float(result.stdout.strip())
            # Add a small buffer between segments (0.3s)
            segment_durations.append(duration + 0.3)
        except:
            # Fallback if duration detection fails
            segment_durations.append(len(sentences[i]) * 0.075)
            
        processed_audio_files.append(processed_path)

    # 3. Create a silence file for padding between segments
    silence_path = os.path.join(temp_dir, "silence.mp3")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
        '-t', '0.3', '-q:a', '9', '-acodec', 'libmp3lame', silence_path
    ], check=True)
    
    # 4. Combine with silences between segments
    concat_file = os.path.join(temp_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for i, audio_file in enumerate(processed_audio_files):
            f.write(f"file '{audio_file}'\n")
            # Add silence after all but the last segment
            if i < len(processed_audio_files) - 1:
                f.write(f"file '{silence_path}'\n")
    
    # Use concat demuxer with copy codec
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_file, 
        '-c', 'copy',
        output_path
    ], check=True)

    # Save segment durations
    durations_file = os.path.join(temp_dir, "segment_durations.txt")
    with open(durations_file, 'w') as f:
        for duration in segment_durations:
            f.write(f"{duration}\n")

    return output_path, durations_file

# Create subtitles using OpenCV
def create_subtitles_opencv(sentences: List[str], background_clips, audio_duration: float, 
                           segment_durations: List[float] = None) -> List[VideoFileClip]:
    """Create subtitle clips using OpenCV instead of MoviePy's TextClip."""
    temp_dir = tempfile.mkdtemp()  # Add this line to create temporary directory
    subtitle_clips = []
    current_time = 0
    subtitle_files = []

    # Get video dimensions from first background clip
    first_clip = background_clips[0]
    width, height = first_clip.size

    # Create subtitle for each sentence
    for i, sentence in enumerate(sentences):
        # Get the appropriate duration for this segment
        if segment_durations and i < len(segment_durations):
            segment_duration = segment_durations[i]
        else:
            # Fallback to even distribution if no durations provided
            segment_duration = audio_duration / len(sentences)
        
        # Calculate timing
        start_time = current_time
        end_time = min(start_time + segment_duration, audio_duration) 
        current_time = end_time

        # Find which background clip(s) this subtitle overlaps with
        overlapping_clips = []
        for clip in background_clips:
            if (clip.start <= end_time and clip.start + clip.duration >= start_time):
                overlapping_clips.append(clip)

        if not overlapping_clips:
            continue
            
        # THIS WAS MISSING - Wrap text to fit on screen
        wrapped_text = textwrap.fill(sentence, width=25)  # Wrap at 25 chars per line

        # Create frames with subtitles for this segment
        output_path = os.path.join(temp_dir, f"subtitle_{i}.mp4")

        # We'll create a subtitle video by extracting frames from the background,
        # adding text, and writing a new video
        fps = overlapping_clips[0].fps
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Split the wrapped text into lines
        text_lines = wrapped_text.split('\n')

        # Calculate number of frames for this segment
        num_frames = int(segment_durations[i] * fps)

        for frame_idx in range(num_frames):
            # Calculate the exact time for this frame
            frame_time = start_time + (frame_idx / fps)

            # Find which background clip this frame belongs to
            bg_clip = None
            for clip in overlapping_clips:
                if clip.start <= frame_time < clip.start + clip.duration:
                    bg_clip = clip
                    break

            if bg_clip is None:
                continue

            # Get the frame from the background clip
            local_time = frame_time - bg_clip.start
            frame = bg_clip.get_frame(local_time)

            # Convert from RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Add subtitle text to the frame
            text_size = 1.0  # Smaller font (reduced from 1.2)
            y_offset = height - 180  # Higher position to fit more lines
            
            for line in text_lines:
                # Calculate text width to center it properly
                (text_width, _), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, text_size, 2)
                text_x = (width - text_width) // 2  # Center text
                
                # Make outline more visible
                for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                    cv2.putText(frame, line, (text_x + dx, y_offset + dy),
                              cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), 5, cv2.LINE_AA)

                # Add white text
                cv2.putText(frame, line, (text_x, y_offset),
                          cv2.FONT_HERSHEY_SIMPLEX, text_size, (255, 255, 255), 2, cv2.LINE_AA)
                y_offset += 40  # Spacing between lines

            # Write the frame
            video_writer.write(frame)

        video_writer.release()

        # Create a VideoFileClip from the output file
        subtitle_clip = VideoFileClip(output_path)
        subtitle_clip = subtitle_clip.set_start(start_time)
        subtitle_files.append(output_path)
        subtitle_clips.append(subtitle_clip)

    return subtitle_clips, subtitle_files

# Main function to generate brain rot video
def generate_brain_rot_video(lecture_text: str, output_path: str) -> None:
    """Generate a brain rot video from CS lecture content."""
    # Process the lecture content
    print("Processing lecture content...")
    sentences = process_lecture_content(lecture_text)

    # Get background videos
    #background_videos = get_background_videos(3)

    # With this (replace with your actual file path):
    background_videos = ["videoplayback.mp4"]

    if not background_videos:
        print("Failed to get any background videos. Exiting.")
        sys.exit(1)

    # Generate TTS audio
    print("Generating TTS audio...")
    temp_audio_path = os.path.join(tempfile.mkdtemp(), "combined_audio.mp3")
    audio_path, durations_file = generate_tts_audio(sentences, temp_audio_path)  # Get durations too
    audio_clip = AudioFileClip(audio_path)
    
    # Load segment durations for accurate subtitle timing
    segment_durations = []
    with open(durations_file, 'r') as f:
        for line in f:
            segment_durations.append(float(line.strip()))

    # Load and process background videos
    print("Processing background videos...")
    background_clips = []
    current_time = 0

    for video_path in background_videos:
        try:
            clip = VideoFileClip(video_path)

            # If clip is longer than remaining audio, trim it
            clip_duration = min(clip.duration, audio_clip.duration - current_time)
            if clip_duration <= 0:
                continue

            # Trim and set position in timeline
            trimmed_clip = clip.subclip(0, clip_duration).set_start(current_time)
            background_clips.append(trimmed_clip)
            current_time += clip_duration

            # If we have enough background footage, stop
            if current_time >= audio_clip.duration:
                break
        except Exception as e:
            print(f"Error processing video {video_path}: {e}")

    # If we don't have enough footage, loop the last video
    if current_time < audio_clip.duration and background_clips:
        last_clip = VideoFileClip(background_videos[-1])
        remaining_duration = audio_clip.duration - current_time

        while remaining_duration > 0:
            clip_duration = min(last_clip.duration, remaining_duration)
            trimmed_clip = last_clip.subclip(0, clip_duration).set_start(current_time)
            background_clips.append(trimmed_clip)
            current_time += clip_duration
            remaining_duration -= clip_duration

    # If we still don't have any background clips, create a simple one
    if not background_clips:
        print("Failed to process any background videos. Creating a simple background...")
        temp_dir = tempfile.mkdtemp()
        simple_bg_path = os.path.join(temp_dir, "simple_background.mp4")
        create_simple_background_video(simple_bg_path, duration=audio_clip.duration)
        bg_clip = VideoFileClip(simple_bg_path)
        bg_clip = bg_clip.set_start(0)
        background_clips = [bg_clip]

    # Create composite background video
    background_composite = CompositeVideoClip(background_clips)

    # Create subtitles using OpenCV
    print("Creating subtitles...")
    try:
        subtitle_clips, subtitle_files = create_subtitles_opencv(sentences, background_clips, 
                                                           audio_clip.duration, segment_durations)

        # Final composite with audio and subtitles
        print("Creating final video...")
        final_clips = [background_composite] + subtitle_clips
        final_clip = CompositeVideoClip(final_clips)
        final_clip = final_clip.set_audio(audio_clip)

        # Write output file
        print(f"Writing video to {output_path}...")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24
        )

        print(f"Brain rot video successfully generated: {output_path}")

        # Clean up
        for clip in background_clips:
            clip.close()
        for clip in subtitle_clips:
            clip.close()
        audio_clip.close()
        final_clip.close()

        # Clean up temporary subtitle files
        for file in subtitle_files:
            try:
                os.remove(file)
            except:
                pass

    # Fallback method if the OpenCV approach fails
    except Exception as e:
        print(f"Error with OpenCV subtitles: {e}")
        print("Falling back to direct video creation without TextClip...")

        # Create a video without subtitles
        print("Creating video without subtitles...")
        final_clip = background_composite.set_audio(audio_clip)

        # Write output file
        print(f"Writing video to {output_path}...")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24
        )

        print(f"Video generated without subtitles: {output_path}")
        print("You can add subtitles manually using a video editor.")

        # Clean up
        for clip in background_clips:
            clip.close()
        audio_clip.close()
        final_clip.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read from file if provided as argument
        with open(sys.argv[1], 'r') as f:
            lecture_text = f.read()
    else:
        # Otherwise prompt for input
        print("Enter CS lecture content (press Ctrl+D when finished):")
        lecture_text = sys.stdin.read()

    output_path = "cs_lecture_brain_rot.mp4"
    generate_brain_rot_video(lecture_text, output_path)
