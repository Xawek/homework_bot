
class SendMessageException(Exception):
    """Проблема с отправкой сообщения."""


class ResponseProblemException(Exception):
    """Ошибка ответа API."""


class RequestProblemException(Exception):
    """Ошибка запроса к API."""


class ConnectionError(Exception):
    """Эндпоинт не доступен."""
