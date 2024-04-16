"""Speech module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import requests  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from logging import Logger


def speech2text(
    oauth_token: str,
    audio_file_path: str,
    logger: Logger,
) -> tuple[int, str]:
    """Speech to text.

    Params.
    ------
    oauth_token: str
        oauth token
    audio_file_path: str
        path to audio file
    logger: CustomLogger
        logger

    Returns
    -------
    tuple[int, str]: status code and text

    """
    base_url = "https://smartspeech.sber.ru/rest/v1/speech:recognize"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "audio/mpeg",
    }
    ok_code = 200

    with Path(audio_file_path).open("rb") as audio_file:
        data = audio_file.read()

    response = requests.post(
        base_url,
        headers=headers,
        data=data,
        verify=False,  # noqa: S501
        timeout=10,
    )

    if response.status_code != ok_code:
        logger.error(str(response.json()), "openai")
        return response.status_code, ""

    logger.info("Speech to text successful.", extra={"message_type": "openai"})
    return ok_code, " ".join(response.json()["result"])
