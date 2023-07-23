from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import crop
import os
import string
from textwrap import wrap
import re
import random
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()


def create_video(
    subs,
    title,
    audio_file_path="gs://tiktok-video-generator-tts/temp.wav",  # Assume this is your GCS path
    footage_directory="./footage/",
):
    # Initialize a GCS client
    storage_client = storage.Client()

    # Download the audio file from GCS
    local_audio_file_path = "./temp/temp.wav"  # Temporarily save the audio file locally
    bucket_name, blob_name = audio_file_path[5:].split(
        "/", 1
    )  # Split GCS path to bucket name and blob name
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_audio_file_path)

    # Create an AudioFileClip from the downloaded wav file
    audio = AudioFileClip(local_audio_file_path)

    # Get the duration of the audio
    audio_duration = audio.duration

    # List all the mp4 files in the directory
    video_files = [f for f in os.listdir(footage_directory) if f.endswith(".mp4")]

    if not video_files:
        raise ValueError(f"No .mp4 files found in {footage_directory}.")

    # Randomly select a video file
    video_file_path = os.path.join(footage_directory, random.choice(video_files))

    # Load the video
    clip = VideoFileClip(video_file_path)

    # Ensure the audio file fits in the video duration
    if clip.duration < audio_duration:
        raise ValueError(f"The selected video is too short for the audio.")

    # Randomly select a start time for the clip such that the remaining duration is at least as long as the audio
    start_time = random.uniform(0, clip.duration - audio_duration)

    # Cut the video to fit the duration of the audio
    clip = clip.subclip(start_time, start_time + audio_duration)

    # Assume that we already have the dimensions of the video
    original_width = clip.size[0]
    original_height = clip.size[1]

    # We want a 9:16 aspect ratio, so we calculate the new height
    new_height = original_width * (16 / 9)
    # If the new height is larger than the original height, we need to decrease the width instead
    if new_height > original_height:
        new_width = original_height * (9 / 16)
        new_height = original_height
    else:
        new_width = original_width

    # Now we can crop the video
    clip_cropped = crop(
        clip,
        width=int(new_width),
        height=int(new_height),
        x_center=clip.w / 2,
        y_center=clip.h / 2,
    )

    # Resize the cropped video clip to have a height of 720px and a 9:16 aspect ratio
    clip_resized = clip_cropped.resize(height=720, width=720 * (9 / 16))

    # Function to generate subtitles
    def generator(txt):
        clip_width = 0.5 * new_width
        wrapped_text = "\n".join(wrap(txt, width=int(clip_width / 13)))
        font_size = 50  # adjust this as needed
        outline_width = 4  # adjust this as needed for the shadow width
        shadow_offset = (1, 3)  # adjust this as needed for the shadow offset
        # Check for the special formatting and apply colors accordingly
        colored_texts = []
        split_text = wrapped_text.split()
        for word in split_text:
            if re.match(r"`.*`", word):  # If the word is surrounded by back-ticks
                # Remove the back-ticks and create a TextClip with purple color
                word = re.sub(r"`", "", word)  # Remove back-ticks
                text_clip = TextClip(
                    word,
                    fontsize=font_size,
                    font="src/font.ttf",
                    color="#8423d9",
                ).set_pos("center", "bottom")
                outline_clip = (
                    TextClip(
                        word,
                        fontsize=font_size + outline_width,
                        font="src/font.ttf",
                        color="black",
                    )
                    .set_pos(("center", "bottom"), relative=True)
                    .set_position(shadow_offset, relative=True)
                )
            else:
                # For normal text, create a TextClip with white color
                text_clip = TextClip(
                    word,
                    fontsize=font_size,
                    font="src/font.ttf",
                    color="white",
                ).set_pos("center", "bottom")
                outline_clip = (
                    TextClip(
                        word,
                        fontsize=font_size + outline_width,
                        font="src/font.ttf",
                        color="black",
                    )
                    .set_pos(("center", "bottom"), relative=True)
                    .set_position(shadow_offset, relative=True)
                )
            colored_texts.append(outline_clip)
            colored_texts.append(text_clip)

        # Combine all the TextClips into a CompositeVideoClip
        return CompositeVideoClip(colored_texts)

    # Create a SubtitlesClip
    subtitles = SubtitlesClip(subs, generator)

    # Overlay the subtitles on the video and add the audio
    final_clip = CompositeVideoClip(
        [clip_resized, subtitles.set_position(("center"))]
    ).set_audio(audio)

    # Write the result to a file
    final_clip.write_videofile(f"videos/{title}.mp4")

    # Clean up the temporary files
    delete_blob("tiktok-video-generator-tts", "temp.wav")
    os.remove(local_audio_file_path)  # Remove the downloaded audio file


def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print("Blob {} deleted.".format(blob_name))
