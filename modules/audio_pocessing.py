from pydub import AudioSegment  # type: ignore
from pydub.silence import split_on_silence  # type: ignore
import os
from modules.logger import CustomLogger


class AudioProcessing:
    def __init__(self, logger: CustomLogger) -> None:
        self.logger = logger

    def convert_to_mp3(self, file_path: str) -> tuple[int, str]:
        audio = AudioSegment.from_ogg(file_path)

        # save to mp3
        try:
            new_path = file_path.replace(".ogg", ".mp3")
            audio.export(new_path, format="mp3")
            os.remove(file_path)
            self.logger.info(f"Converted {file_path} to {new_path}.", "server")
        except Exception as e:
            self.logger.error(str(e), "server")
            return 500, ""

        return 200, new_path

    def to_chunks(self, file_path: str, user_id: int) -> int:

        os.mkdir(f"chunks/{user_id}")

        try:
            audio = AudioSegment.from_mp3(file_path)
            chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)

            for ind, chunk in enumerate(chunks):
                chunk.export(f"chunks/{user_id}/{ind}.mp3", format="mp3")

            os.remove(file_path)
            self.logger.info(f"Converted {file_path} to chunks.", "server")

            return 200
        except Exception as e:
            self.logger.error(str(e), "server")
            return 500
