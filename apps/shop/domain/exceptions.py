class ShopDomainException(Exception):
    """
    Базовая ошибка магазина.
    """
    error_code = 'SHOP_ERROR'
    message = 'Ошибка магазина'
    status_code = 400

    def __init__(self, message=None, details=None):
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


class EmptyCart(ShopDomainException):
    error_code = 'EMPTY_CART'
    message = 'Корзина пуста.'
    status_code = 400


class NotEnoughStock(ShopDomainException):
    error_code = 'NOT_ENOUGH_STOCK'
    message = 'Недостаточно товара на складе.'
    status_code = 400


class ProductNotFound(ShopDomainException):
    error_code = 'PRODUCT_NOT_FOUND'
    message = 'Товар не найден.'
    status_code = 404


class InvalidQuantity(ShopDomainException):
    error_code = 'INVALID_QUANTITY'
    message = 'Количество должно быть натуральным числом.'
    status_code = 400