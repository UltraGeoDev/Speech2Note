"""Audio Processing module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydub import AudioSegment  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from logging import Logger


class AudioProcessing:
    """Class for processing audio files."""

    def __init__(self: AudioProcessing, splt_timeout: int, logger: Logger) -> None:
        """Initialize AudioProcessing.

        Params
        ---
        self: AudioProcessing
        logger: CustomLogger
        splt_timeout: int
        """
        self.logger = logger
        self.splt_timeout = splt_timeout * 1000

    def convert_to_mp3(self: AudioProcessing, file_path: str) -> tuple[int, str]:
        """Get mp3 from ogg.

        Args:
        ----
            self: AudioProcessing
            file_path (str): file path

        Returns:
        -------
            tuple[int, str]: status code and path to mp3

        """
        audio = AudioSegment.from_file(file_path)
        audio_path = Path(file_path)
        suffix = audio_path.suffix

        # save to mp3
        try:
            audio_path = audio_path.with_suffix(".mp3")
            audio.export(audio_path, format="mp3")

            if suffix != ".mp3":
                Path(file_path).unlink()

            new_path = str(audio_path)
            self.logger.info("converted to mp3", extra={"message_type": "server"})
        except Exception:  # noqa: BLE001
            self.logger.info("converted to mp3 error", "server")  # noqa: PLE1205
            return 500, ""

        return 200, new_path

    def to_chunks(self: AudioProcessing, file_path: str, user_id: int) -> int:
        """Split audio file into chunks.

        Args:
        ----
            self: AudioProcessing
            file_path (str): file path
            user_id (int): user id

        Returns:
        -------
            int: status code

        """
        Path(f"data/chunks/{user_id}").mkdir()

        try:
            audio = AudioSegment.from_mp3(file_path)
            for ind, start_time in enumerate(range(0, len(audio), self.splt_timeout)):
                chunk = audio[start_time : start_time + self.splt_timeout]
                chunk.export(f"data/chunks/{user_id}/{ind}.mp3", format="mp3")
            Path(file_path).unlink()
            self.logger.info("Converted to chunks.", extra={"message_type": "server"})
        except Exception as e:  # noqa: BLE001
            self.logger.error(str(e), "server")  # noqa: TRY400
            return 500
        else:
            return 200
