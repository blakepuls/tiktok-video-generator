# Import the files from ./utils
import utils.story as story
import utils.tts as tts
import utils.video as video
import utils.formatting as formatting
from tiktok_uploader.upload import upload_video, upload_videos

import os
from moviepy.config import change_settings
from dotenv import load_dotenv


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service_account.json"

change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGEMAGIC_PATH")})


def main(topic=None):
    title, content, description, gender = story.generate_story(topic)

    paragraph = f"{title}. {content}"

    speech_marks = tts.generate_audio_and_subtitles(paragraph, gender)
    video.create_video(speech_marks, title)

    upload_video(
        f"videos/{title}.mp4",
        description=description,
        cookies="cookies.txt",
        browser="chrome",
    )


if __name__ == "__main__":
    import argparse

    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topic", help="Enter a topic for the video")
    args = parser.parse_args()

    main(args.topic)
