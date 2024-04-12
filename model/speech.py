import requests  # type: ignore
from modules.logger import CustomLogger


def speech2text(
    oauth_token: str, audio_file_path: str, logger: CustomLogger
) -> tuple[int, str]:
    base_url = "https://smartspeech.sber.ru/rest/v1/speech:recognize"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "audio/mpeg",
    }

    with open(audio_file_path, "rb") as audio_file:
        data = audio_file.read()

    response = requests.post(base_url, headers=headers, data=data, verify=False)

    if response.status_code != 200:
        logger.error(str(response.json()), "openai")
        return response.status_code, ""

    logger.info("Speech to text successful.", "openai")
    return 200, " ".join(response.json()["result"])
