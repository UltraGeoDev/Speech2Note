import requests  # type: ignore
import uuid


def get_token(auth_data: str, scope: str) -> str:
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = {"scope": scope}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": f"{uuid.uuid4()}",
        "Authorization": f"Basic {auth_data}",
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    token = response.json().get("access_token")
    if token is None:
        raise ValueError("Failed to get token.")
    return token  # type: ignore
