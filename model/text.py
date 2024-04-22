"""Text module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import requests  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from logging import Logger


def text2note(
    oauth_token: str,
    instruction: str,
    logger: Logger,
    text: str,
    messages: list[dict[str, str]] | None = None,
) -> tuple[int, list[dict[str, str]]]:
    """Text to note.

    Params.
    ------
    oauth_token: str
        oauth token
    text: str
        text
    instruction: str
        instruction
    logger: CustomLogger
        logger

    Returns
    -------
    tuple[int, str]: status code and text

    """
    messages = (
        [
            {"role": "system", "content": instruction},
            {"role": "user", "content": text},
        ]
        if messages is None
        else messages
    )

    base_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {oauth_token}",
    }

    body = {
        "model": "GigaChat",
        "messages": messages,
    }

    response = requests.post(
        base_url,
        headers=headers,
        json=body,
        verify=False,  # noqa: S501
        timeout=10,
    )
    if not response.ok:
        logger.error(str(response.json()), "openai")
        return response.status_code, []

    logger.info("Text to note successful.", extra={"message_type": "text2note"})
    messages.append(response.json()["choices"][0]["message"])
    return 200, messages
