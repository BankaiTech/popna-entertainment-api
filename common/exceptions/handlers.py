"""Centralized exception handling for Popna API."""
import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied as DRFPermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Returns a consistent error envelope:
      { "success": false, "message": "...", "errors": {...} }
    """
    # Let DRF handle the response first for its own exceptions
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data
        message = _extract_message(errors, exc)
        response.data = {
            'success': False,
            'message': message,
            'errors': errors if isinstance(errors, dict) else {'detail': errors},
        }
        return response

    # Handle Django built-in exceptions not covered by DRF
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                'success': False,
                'message': 'Validation error.',
                'errors': {'detail': exc.messages},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                'success': False,
                'message': 'Permission denied.',
                'errors': {'detail': str(exc)},
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Unhandled exceptions — log and return 500
    logger.exception('Unhandled exception: %s', exc, exc_info=True)
    return Response(
        {
            'success': False,
            'message': 'An unexpected error occurred. Please try again.',
            'errors': {},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_message(errors, exc):
    """Extract a human-readable message from error data."""
    if isinstance(exc, NotAuthenticated):
        return 'Authentication credentials were not provided.'
    if isinstance(exc, AuthenticationFailed):
        return 'Invalid authentication credentials.'
    if isinstance(exc, DRFPermissionDenied):
        return 'You do not have permission to perform this action.'
    if isinstance(exc, NotFound):
        return 'The requested resource was not found.'
    if isinstance(exc, ValidationError):
        if isinstance(errors, dict):
            first_key = next(iter(errors), None)
            if first_key:
                val = errors[first_key]
                if isinstance(val, list) and val:
                    return str(val[0])
        return 'Validation error.'
    if isinstance(errors, dict) and 'detail' in errors:
        return str(errors['detail'])
    return 'An error occurred.'
