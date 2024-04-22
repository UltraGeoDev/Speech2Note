"""Audio Processing module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydub import AudioSegment  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from logging import Logger


class AudioProcessing:
    """Class for processing audio files."""

    def __init__(self: AudioProcessing, logger: Logger) -> None:
        """Initialize AudioProcessing.

        Params
        ---
        self: AudioProcessing
            self
        logger: CustomLogger
            logger
        """
        self.logger = logger

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

        # save to mp3
        try:
            new_path = file_path.replace(".ogg", ".mp3")
            audio.export(new_path, format="mp3")
            Path(file_path).unlink()
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
            for ind, start_time in enumerate(range(0, len(audio), 45000)):
                chunk = audio[start_time : start_time + 45000]
                chunk.export(f"data/chunks/{user_id}/{ind}.mp3", format="mp3")
            Path(file_path).unlink()
            self.logger.info("Converted to chunks.", extra={"message_type": "server"})
        except Exception as e:  # noqa: BLE001
            self.logger.error(str(e), "server")  # noqa: TRY400
            return 500
        else:
            return 200
