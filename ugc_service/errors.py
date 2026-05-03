from flask import jsonify, Response
from typing import Tuple


class UgcException(Exception):
    """
    Базовая ошибка UGC-сервиса.
    """
    error_code = 'UGC_ERROR'
    message = 'Ошибка UGC-сервиса'
    status_code = 400

    def __init__(self, message=None, details=None):
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(UgcException):
    error_code = 'VALIDATION_ERROR'
    message = 'Некорректные входные данные.'
    status_code = 400


class ProductNotFound(UgcException):
    error_code = 'PRODUCT_NOT_FOUND'
    message = 'Товар не найден.'
    status_code = 404


class DjangoServiceUnavailable(UgcException):
    error_code = 'DJANGO_SERVICE_UNAVAILABLE'
    message = 'Сервис товаров недоступен.'
    status_code = 503


class ReviewNotFound(UgcException):
    error_code = 'REVIEW_NOT_FOUND'
    message = 'Отзыв не найден. '
    status_code = 404


class InvalidStatus(UgcException):
    error_code = 'INVALID_STATUS'
    message = 'Некорректный статус отзыва.'
    status_code = 400


def error_response(error: UgcException) -> Tuple[Response, int]:
    """
    Преобразует доменную ошибку в HTTP-ответ.
    """
    return jsonify({
        'error_code': error.error_code,
        'message': error.message,
        'details': error.details,
    }), error.status_code