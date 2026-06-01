from typing import Any

import requests
from flask import session

from frontend.settings import REQUEST_TIMEOUT


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def extract_error_message(response: requests.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return f"Ошибка {response.status_code}: {response.text or 'пустой ответ сервера'}"

    if isinstance(data, dict):
        detail = data.get("detail")
        if isinstance(detail, str):
            return detail

        message = data.get("message")
        details = data.get("details")
        if isinstance(message, str) and isinstance(details, dict) and details:
            joined = "; ".join(f"{key}: {value}" for key, value in details.items())
            return f"{message} {joined}"
        if isinstance(message, str):
            return message

        fragments: list[str] = []
        for key, value in data.items():
            if isinstance(value, list):
                fragments.append(f"{key}: {', '.join(str(item) for item in value)}")
            elif isinstance(value, dict):
                nested = ", ".join(f"{nested_key}: {nested_value}" for nested_key, nested_value in value.items())
                fragments.append(f"{key}: {nested}")
            else:
                fragments.append(f"{key}: {value}")
        if fragments:
            return "; ".join(fragments)

    if isinstance(data, list):
        return "; ".join(str(item) for item in data)

    return f"Ошибка {response.status_code}"


def api_request(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    expected_statuses: tuple[int, ...] = (200,),
) -> Any:
    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            headers=headers or {},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as error:
        raise ApiError(f"Не удалось связаться с сервисом: {error}") from error

    if response.status_code not in expected_statuses:
        if response.status_code == 401:
            session.clear()
            raise ApiError("Сессия истекла, войдите заново", status_code=401)
        raise ApiError(extract_error_message(response), status_code=response.status_code)

    if not response.content:
        return {}

    try:
        return response.json()
    except ValueError as error:
        raise ApiError("Сервер вернул ответ не в json формате") from error


def get_service_status(url: str) -> dict[str, str]:
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return {"ok": "true", "label": "online"}
        return {"ok": "false", "label": "error"}
    except requests.RequestException:
        return {"ok": "false", "label": "offline"}
