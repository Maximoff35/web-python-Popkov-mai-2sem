from rest_framework.response import Response
from apps.shop.domain.exceptions import ShopDomainException

def domain_exception_response(error: ShopDomainException) -> Response:
    return Response(
        {
            'error_code': error.error_code,
            'message': error.message,
            'details': error.details,
        },
        status=error.status_code,
    )