from google.cloud import texttospeech
from gtts import gTTS


def save(text, path):
    try:
        gTTS(text).save(path)
    except BaseException as err:
        if "gTTSError" in err.__class__.__name__:
            client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

            with open(path, "wb") as out:
                out.write(response.audio_content)

        else:
           print("Cannot create voice.")
