import requests  # type: ignore
from modules.logger import CustomLogger


def text2note(
    oauth_token: str, text: str, instruction: str, logger: CustomLogger
) -> tuple[int, str]:

    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": text},
    ]

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

    response = requests.post(base_url, headers=headers, json=body, verify=False)
    if response.status_code != 200:
        logger.error(str(response.json()), "openai")
        return response.status_code, ""

    logger.info("Text to note successful.", "openai")
    return 200, response.json()["choices"][0]["message"]["content"]
