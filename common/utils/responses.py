"""Standard API response helpers."""
from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message='', http_status=status.HTTP_200_OK):
    """Return a standard success envelope."""
    payload = {'success': True}
    if message:
        payload['message'] = message
    if data is not None:
        payload['data'] = data
    return Response(payload, status=http_status)


def created_response(data=None, message='Created successfully.'):
    """Shortcut for 201 Created."""
    return success_response(data=data, message=message, http_status=status.HTTP_201_CREATED)


def no_content_response():
    """Shortcut for 204 No Content."""
    return Response(status=status.HTTP_204_NO_CONTENT)


def error_response(message='An error occurred.', errors=None, http_status=status.HTTP_400_BAD_REQUEST):
    """Return a standard error envelope."""
    payload = {
        'success': False,
        'message': message,
        'errors': errors or {},
    }
    return Response(payload, status=http_status)
