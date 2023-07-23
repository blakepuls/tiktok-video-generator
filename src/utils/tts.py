from google.cloud import texttospeech
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import io
import random


from google.cloud import texttospeech
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import io
import random


def format_subs(subs):
    modified_subs = []
    for i in range(len(subs)):
        word = subs[i][1]
        if word.endswith((".", "!", "?")):
            word = f"`{word}`"
        modified_subs.append((subs[i][0], word))
    return modified_subs


def generate_audio_and_subtitles(
    paragraph, gender="neutral", output_dir="./temp/", output_name="temp"
):
    print("Generating audio and subtitles...")

    # Initialize a TTS client
    tts_client = texttospeech.TextToSpeechClient()

    # Initialize a STT client
    stt_client = speech.SpeechClient()

    # Initialize a GCS client
    storage_client = storage.Client()

    # Get GCS bucket
    bucket = storage_client.get_bucket("tiktok-video-generator-tts")

    # Map of genders to their corresponding SSML voice gender options
    genders = {
        "male": texttospeech.SsmlVoiceGender.MALE,
        "female": texttospeech.SsmlVoiceGender.FEMALE,
        "neutral": texttospeech.SsmlVoiceGender.NEUTRAL,
    }

    # Validate and normalize the gender input
    gender = gender.lower()
    if gender not in genders:
        raise ValueError("Invalid gender. Choose from 'male', 'female', or 'neutral'.")

    # Get list of voices
    voices_response = tts_client.list_voices()

    # Filter voices based on language and gender
    filtered_voices = [
        voice
        for voice in voices_response.voices
        if voice.ssml_gender == genders[gender] and "en-US" in voice.language_codes
    ]

    if not filtered_voices:
        raise ValueError(f"No voices available for {gender} gender in en-US.")

    # Select a random voice
    voice_name = random.choice(filtered_voices).name

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=genders[gender], name=voice_name
    )

    # Build the audio config
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the TTS request
    response = tts_client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=paragraph),
        voice=voice,
        audio_config=audio_config,
    )

    # Create a blob in GCS
    blob = bucket.blob(f"{output_name}.wav")

    # Upload the synthesized speech to GCS
    blob.upload_from_string(response.audio_content)

    # Now we transcribe the audio file to get the timings

    # Load the audio from GCS
    blob.reload()  # Get the latest state of a Blob

    # Build the audio object using URI
    audio = speech.RecognitionAudio(uri=f"gs://{bucket.name}/{blob.name}")

    # Configure the STT request
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,  # Enable automatic punctuation
    )

    # Perform the STT request
    operation = stt_client.long_running_recognize(config=config, audio=audio)

    response = operation.result(timeout=90)  # You may need to adjust the timeout

    # Process the STT response to get word timings
    subs = []
    for result in response.results:
        alternative = result.alternatives[0]

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()

            subs.append(((start_time, end_time), word))

    return format_subs(subs)


# from google.cloud import texttospeech
# from google.cloud import speech_v1p1beta1 as speech
# import io
# import random


# def format_subs(subs):
#     modified_subs = []
#     for i in range(len(subs)):
#         word = subs[i][1]
#         if word.endswith((".", "!", "?")):
#             word = f"`{word}`"
#         modified_subs.append((subs[i][0], word))
#     return modified_subs


# def generate_audio_and_subtitles(
#     paragraph, gender="neutral", output_dir="./temp/", output_name="temp"
# ):
#     # Initialize a TTS client
#     tts_client = texttospeech.TextToSpeechClient()

#     # Initialize a STT client
#     stt_client = speech.SpeechClient()

#     # Map of genders to their corresponding SSML voice gender options
#     genders = {
#         "male": texttospeech.SsmlVoiceGender.MALE,
#         "female": texttospeech.SsmlVoiceGender.FEMALE,
#         "neutral": texttospeech.SsmlVoiceGender.NEUTRAL,
#     }

#     # Validate and normalize the gender input
#     gender = gender.lower()
#     if gender not in genders:
#         raise ValueError("Invalid gender. Choose from 'male', 'female', or 'neutral'.")

#     # Get list of voices
#     voices_response = tts_client.list_voices()

#     # Filter voices based on language and gender
#     filtered_voices = [
#         voice
#         for voice in voices_response.voices
#         if voice.ssml_gender == genders[gender] and "en-US" in voice.language_codes
#     ]

#     if not filtered_voices:
#         raise ValueError(f"No voices available for {gender} gender in en-US.")

#     # Select a random voice
#     voice_name = random.choice(filtered_voices).name

#     # Build the voice request
#     voice = texttospeech.VoiceSelectionParams(
#         language_code="en-US", ssml_gender=genders[gender], name=voice_name
#     )

#     # Build the audio config
#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.LINEAR16
#     )

#     # Perform the TTS request
#     response = tts_client.synthesize_speech(
#         input=texttospeech.SynthesisInput(text=paragraph),
#         voice=voice,
#         audio_config=audio_config,
#     )

#     # Write the response to a file
#     audio_file_path = f"{output_dir}/{output_name}.wav"
#     with open(audio_file_path, "wb") as out:
#         out.write(response.audio_content)

#     # Now we transcribe the audio file to get the timings

#     # Load the audio into memory
#     with io.open(audio_file_path, "rb") as audio_file:
#         content = audio_file.read()

#     # Configure the STT request
#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         language_code="en-US",
#         enable_word_time_offsets=True,
#         enable_automatic_punctuation=True,  # Enable automatic punctuation
#     )

#     # Build the audio object
#     audio = speech.RecognitionAudio(content=content)

#     # Perform the STT request
#     response = stt_client.recognize(config=config, audio=audio)

#     # Process the STT response to get word timings
#     subs = []
#     print(response.results)
#     for result in response.results:
#         alternative = result.alternatives[0]

#         for word_info in alternative.words:
#             word = word_info.word
#             start_time = word_info.start_time.total_seconds()
#             end_time = word_info.end_time.total_seconds()

#             subs.append(((start_time, end_time), word))

#     return format_subs(subs)
