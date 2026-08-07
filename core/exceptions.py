from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status


class CustomAppException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request'
    default_code = 'BAD_REQUEST'

    def __init__(self, message='Bad request', error_code='BAD_REQUEST',
                 status_code=status.HTTP_400_BAD_REQUEST, errors=None, details=None):
        self.detail = message
        self.status_code = status_code
        self.error_code = error_code
        self.errors = errors or []
        self.extra_details = details


class EntityInUseException(CustomAppException):
    def __init__(self, message, reference_count, can_archive=True):
        super().__init__(
            message=message,
            error_code='ENTITY_IN_USE',
            status_code=status.HTTP_400_BAD_REQUEST,
            details={'reference_count': reference_count, 'can_archive': can_archive},
        )
        self.reference_count = reference_count
        self.can_archive = can_archive


def custom_exception_handler(exc, context):
    if isinstance(exc, CustomAppException):
        content = {
            'success': False,
            'error_code': exc.error_code,
            'message': str(exc.detail),
        }
        if exc.errors:
            content['errors'] = exc.errors
        if exc.extra_details:
            content['details'] = exc.extra_details
        return Response(content, status=exc.status_code)

    response = exception_handler(exc, context)

    if response is not None:
        sc = response.status_code
        if sc == 401:
            error_code = 'UNAUTHORIZED'
        elif sc == 403:
            error_code = 'FORBIDDEN'
        elif sc == 404:
            error_code = 'NOT_FOUND'
        elif sc == 405:
            error_code = 'METHOD_NOT_ALLOWED'
        else:
            error_code = 'HTTP_ERROR'

        detail = response.data.get('detail', str(response.data)) if isinstance(response.data, dict) else str(response.data)

        response.data = {
            'success': False,
            'error_code': error_code,
            'message': detail,
            'errors': [],
        }
        return response

    # Unhandled exception
    return Response(
        {
            'success': False,
            'error_code': 'INTERNAL_SERVER_ERROR',
            'message': 'Kutilmagan server xatoligi yuz berdi',
            'errors': [{'field': 'server', 'message': str(exc)}],
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
