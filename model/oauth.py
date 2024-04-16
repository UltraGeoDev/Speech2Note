"""OAuth module."""

import uuid

import requests  # type: ignore[import-untyped]


def get_token(auth_data: str, scope: str) -> str:
    """Get OAuth token.

    Params.
    ------
    auth_data: str
        auth data
    scope: str
        scope

    Returns
    -------
    str: OAuth token

    """
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = {"scope": scope}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": f"{uuid.uuid4()}",
        "Authorization": f"Basic {auth_data}",
    }

    response = requests.post(
        url,
        headers=headers,
        data=payload,
        verify=False,  # noqa: S501
        timeout=10,
    )
    token = response.json().get("access_token")
    if token is None:
        msg = "Failed to get token."
        raise ValueError(msg)
    return token  # type: ignore[no-any-return]
