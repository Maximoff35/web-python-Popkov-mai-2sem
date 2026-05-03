from ugc_service.errors import ValidationError


def validate_review_create_data(data: dict) -> dict:
    """
    Валидирует данные при создании отзыва.
    Возвращает очищенные данные.
    """
    if not isinstance(data, dict):
        raise ValidationError(details={'body': 'Тело запроса должно быть JSON-объектом.'})

    product_id = data.get('product_id')
    user_name = data.get('user_name')
    text = data.get('text')
    rating = data.get('rating')

    errors = {}
    if product_id is None:
        errors['product_id'] = 'Обязательное поле.'
    elif not isinstance(product_id, int):
        errors['product_id'] = 'Должно быть целым числом.'

    if user_name is None:
        errors['user_name'] = 'Обязательное поле.'
    elif not isinstance(user_name, str):
        errors['user_name'] = 'Должно быть строкой.'
    elif not user_name.strip():
        errors['user_name'] = 'Не может быть пустым.'
    elif len(user_name.strip()) > 100:
        errors['user_name'] = 'Максимальная длина - 100 символов.'

    if text is None:
        errors['text'] = 'Обязательное поле.'
    elif not isinstance(text, str):
        errors['text'] = 'Должно быть строкой.'
    elif not text.strip():
        errors['text'] = 'Не может быть пустым.'
    elif len(text.strip()) < 5:
        errors['text'] = 'Минимальная длина - 5 символов.'
    elif len(text.strip()) > 1000:
        errors['text'] = 'Максимальная длина - 1000 символов.'

    if rating is None:
        errors['rating'] = 'Обязательное поле.'
    elif not isinstance(rating, int):
        errors['rating'] = 'Должно быть целым числом.'
    elif rating < 1 or rating > 5:
        errors['rating'] = 'Должно быть числом от 1 до 5.'

    if errors:
        raise ValidationError(details=errors)

    return {
        'product_id': product_id,
        'user_name': user_name.strip(),
        'text': text.strip(),
        'rating': rating,
    }

def validate_product_id_query(value):
    """
    Валидирует product_id из query-параметров.
    """
    if value is None:
        return None
    try:
        product_id = int(value)
    except ValueError:
        raise ValidationError(details={'product_id': 'Должно быть целым числом.'})
    if product_id <= 0:
        raise ValidationError(details={'product_id': 'Должно быть натуральным числом.'})
    return product_id