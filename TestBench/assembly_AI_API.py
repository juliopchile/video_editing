import os
import json
import logging
from enum import Enum
from typing import Any
import assemblyai as aai
from assemblyai import TranscriptionConfig, Settings, TranscriptStatus

logger = logging.getLogger(__name__)

# ── CONFIGURATION ──────────────────────────────────────────────────────────
API_KEY = ""
BASE_URL = "https://api.assemblyai.com"
EU_URL = "https://api.eu.assemblyai.com"
CUSTOM_SPELLING = {
  "yang": ("yang"),
  "FMS": ("efe eme ese"),
  "freestyle": ("fristail", "fristeil"),
  "Bnet": ("benet", "bennet", "venet", "vennet"),
}

# By default use this configurations
TRANSCRIPTION_CONFIG = TranscriptionConfig(
    language_code="es",
    speaker_labels=True,
    punctuate=True,
    format_text=True,
    filter_profanity=False,
    disfluencies=False,
    custom_spelling=CUSTOM_SPELLING,
)

SETTINGS = Settings(
    api_key=API_KEY,
    base_url=BASE_URL
)

ERROR: dict[str, str] = {
    "settings": "Settings must be a dictionary or an instance of Settings.",
    "api_key": "API key must be a string.",
    "config": ("Configuration must be a dictionary or an instance of "
               "TranscriptionConfig."),
}

# ── CUSTOM CLASSES ──────────────────────────────────────────────────────────
class TranscriptionError(Exception):
    """Custom exception for transcription-related errors"""
    pass

class ExportFormat(str, Enum):
    """
    Enum for export formats.
    """
    SRT = "srt"
    VTT = "vtt"
    TXT = "txt"
    TEXT = "text"
    WRD = "wrd"
    WORD = "word"
    SENT = "sent"
    SENTENCES = "sentences"
    PARA = "para"
    PARAGRAPH = "paragraph"
    

class AssemblyAI:
    """
    A class to interact with AssemblyAI API for audio transcription.
    """
    def __init__(self,
                 api_key: str | None = API_KEY,
                 settings: dict | Settings | None = SETTINGS,
                 config: dict | TranscriptionConfig | None = None,
                 transcript_id: str | None = None
                 ) -> None:

        self.api_key: str = api_key if isinstance(api_key, str) else API_KEY
        self.settings: Settings = (
            Settings(**settings) if isinstance(settings, dict)
            else settings if isinstance(settings, Settings)
            else SETTINGS
        )
        self.config: TranscriptionConfig = (
            TranscriptionConfig(**config) if isinstance(config, dict)
            else config if isinstance(config, TranscriptionConfig)
            else TRANSCRIPTION_CONFIG
        )
        self.transcript: aai.Transcript | None = None
        
        if transcript_id is not None:
            self.retrieve_transcription(transcript_id)

    def set_settings(self, settings: dict | Settings) -> None:
        """
        Set the settings for the AssemblyAI instance. This settings are
        used to configure the client in the transcription process.

        :param dict | Settings settings: The settings to be used.
        :raises ValueError: If settings is not a dictionary or an
        instance of Settings.
        """
        if isinstance(settings, dict):
            self.settings = Settings(**settings)
        elif isinstance(settings, Settings):
            self.settings = settings
        else:
            raise ValueError(ERROR["settings"])

    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key to be used by the AssemblyAI instance.
        
        :param str api_key: Your AssemblyAI API key.
        :raises ValueError: If api_key is not a string.
        """
        if isinstance(api_key, str):
            self.api_key = api_key
        else:
            raise ValueError(ERROR["api_key"])
    
    def set_config(self, config: dict | TranscriptionConfig) -> None:
        """
        Set the transcription configuration to be used by the AssemblyAI
        instance when transcribing audio files.
        
        :param dict | TranscriptionConfig config: The configuration to
        be used in the transcription process.
        :raises ValueError: If config is not a dictionary or an instance
        of TranscriptionConfig.
        """
        if isinstance(config, dict):
            self.config = TranscriptionConfig(**config)
        elif isinstance(config, TranscriptionConfig):
            self.config = config
        else:
            raise ValueError(ERROR["config"])
    
    def transcribe(self, audio_file: str) -> None:
        """
        Transcribe the given audio file using AssemblyAI.
        
        :param str audio_file: Path or URL of the audio to transcribe.
        :raises ValueError: If missing configuration is not set.
        :raises TranscriptionError: If transcription process fails.
        :raises RuntimeError: If something else goes wrong.
        """
        if not self.settings:
            raise ValueError("Settings are not set.")
        if not self.config:
            raise ValueError("Transcription configuration is not set.")

        try:
            # Initialize the client with the provided settings
            client = aai.client.Client(settings=self.settings)
            transcriber = aai.Transcriber(client=client, config=self.config)
            logger.info(f"Starting transcription for: {audio_file}")
            # Perform transcription
            transcript = transcriber.transcribe(
                data=audio_file, config=self.config
            )
            # Check transcription status
            if transcript.status == TranscriptStatus.error:
                error = transcript.error
                raise TranscriptionError(f"Transcription failed: {error}")
            else:
                self.transcript = transcript
                logger.info(f"Transcription completed: {transcript.id}")
        except Exception as e:
            raise RuntimeError(f"Transcription error: {e}") from e

    def retrieve_transcription(self, transcript_id: str) -> None:
        """
        Retrieve a transcription by its ID. It initialize a client and
        transcript object that then gets updated. This method doesn't
        use the ``get_by_id()``.

        :param str transcript_id: Transcription ID to retrieve.
        :raises ValueError: If missing configuration is not set.
        :raises TranscriptionError: If the transcription is faulty.
        :raises RuntimeError: If something else goes wrong.
        """
        if not self.settings:
            raise ValueError("Settings are not set.")
        if not self.config:
            raise ValueError("Transcription configuration is not set.")

        try:
            # Initialize the client and transcript with the provided ID
            client = aai.client.Client(settings=self.settings)
            transcript = aai.Transcript(
                transcript_id=transcript_id, client=client
            )
            transcript.wait_for_completion() # Updates the transcript
            # Check transcription status
            if transcript.status == TranscriptStatus.error:
                error = transcript.error
                raise TranscriptionError(f"Transcription failed: {error}")
            else:
                self.transcript = transcript
                logger.info(f"Transcription retrieved: {transcript.id}")
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve transcription: {e}") from e

    def _ensure_transcript(self) -> aai.Transcript:
        if not self.transcript:
            raise ValueError("No transcript available to save.")
        return self.transcript

    def _save_text(self, content: str, filename: str, fmt: str) -> None:
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)
            logger.info(f"\n{fmt} saved as: {filename}")
        except Exception as e:
            raise RuntimeError(f"Failed to export transcription: {e}") from e

    def _save_json(self, data: list[Any], filename: str, fmt: str) -> None:
        if not data:
            raise ValueError(f"No {fmt.lower()} found in transcript.")
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            logger.info(f"\n{fmt} saved as: {filename}")
        except Exception as e:
            raise RuntimeError(f"Failed to export transcription: {e}") from e

    def save_srt(self, filename: str | None = None,
                 chars: int | None = 32) -> None:
        """
        Export the transcription in SRT format.

        :param int | None chars: Max number of characters percaption.
        :raises ValueError: If there is no transcription to process.
        :raises RuntimeError: If something else goes wrong.
        """
        transcript = self._ensure_transcript()
        srt = transcript.export_subtitles_srt(chars_per_caption=chars)
        if filename is None:
            filename = f"transcript_{transcript.id}.srt"
        self._save_text(srt, filename, "SRT subtitles")

    def save_vtt(self, filename: str | None = None,
                 chars: int | None = 32) -> None:
        """
        Export the transcription in VTT format.

        :param int | None chars: Max number of characters percaption.
        :raises ValueError: If there is no transcription to process.
        :raises RuntimeError: If something else goes wrong.
        """
        transcript = self._ensure_transcript()
        vtt = transcript.export_subtitles_vtt(chars_per_caption=chars)
        if filename is None:
            filename = f"transcript_{transcript.id}.vtt"
        self._save_text(vtt, filename, "VTT subtitles")

    def save_txt(self, filename: str | None = None) -> None:
        """
        Export the transcription as plain text with no format.

        :raises ValueError: If there is no transcription to process.
        :raises RuntimeError: If something else goes wrong.
        """
        transcript = self._ensure_transcript()
        txt = str(transcript.text)
        if filename is None:
            filename = f"transcript_{transcript.id}.txt"
        self._save_text(txt, filename, "TXT subtitles")

    def save_paragraphs(self, filename: str | None = None) -> None:
        """
        Export the transcription by paragraph in a JSON format.

        :raises ValueError: If there is no transcription to process.
        :raises ValueError: If no paragraphs found in transcript.
        :raises RuntimeError: If something else goes wrong.
        """
        transcript = self._ensure_transcript()
        paragraphs = transcript.get_paragraphs()
        data = [
            p.dict() if hasattr(p, "dict") else p.__dict__
            for p in (paragraphs or [])
        ]
        if filename is None:
            filename = f"paragraphs_transcript_{transcript.id}.json"
        self._save_json(data, filename, "Paragraphs")

    def save_sentences(self, filename: str | None = None) -> None:
        """
        Export the transcription by sentence in a JSON format.

        :raises ValueError: If there is no transcription to process.
        :raises ValueError: If no sentences found in transcript.
        :raises RuntimeError: If something else goes wrong.
        """
        transcript = self._ensure_transcript()
        sentences = transcript.get_sentences()
        data = [
            s.dict() if hasattr(s, "dict") else s.__dict__
            for s in (sentences or [])
        ]
        if filename is None:
            filename = f"sentences_transcript_{transcript.id}.json"
        self._save_json(data, filename, "Sentences")

    def save_words(self, filename: str | None = None) -> None:
        """
        Export the transcription word by word in a JSON format.

        :raises ValueError: If there is no transcription to process.
        :raises ValueError: If no words are found in transcript.
        :raises RuntimeError: If something else goes wrong.
        """
        transcript = self._ensure_transcript()
        words = transcript.words or [] # Lista de objetos WORD
        data = [w.dict() if hasattr(w, "dict") else w.__dict__ for w in words]
        if filename is None:
            filename =  f"words_transcript_{transcript.id}.json"
        self._save_json(data, filename, "Words")

        
        


if __name__ == '__main__':
    transcript_id = "e82bfc4a-c55e-43b6-a530-12341c770de5"
    assembly_ai = AssemblyAI()
    assembly_ai.retrieve_transcription(transcript_id=transcript_id)
    assembly_ai.save_vtt()
    assembly_ai.save_srt()
    assembly_ai.save_txt()
    assembly_ai.save_paragraphs()
    assembly_ai.save_sentences()
    assembly_ai.save_words()