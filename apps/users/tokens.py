"""
Custom JWT authentication backend.

CustomerUser is a lightweight wrapper around Contact
so it can be used as the `user` object in JWT tokens.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CustomerUser:
    """
    Wraps a Contact object to behave like a Django user for JWT purposes.
    is_customer = True distinguishes it from staff users.
    """

    def __init__(self, contact):
        self.contact = contact
        self.pk = f'customer_{contact.id}'
        self.id = self.pk
        self.is_customer = True
        self.is_active = True
        self.is_authenticated = True
        self.organization_id = contact.organization_id

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.contact.password_hash)

    # AbstractBaseUser compatibility
    def set_password(self, raw_password):
        pass

    @property
    def name(self):
        return self.contact.name


class PopnaJWTAuthentication(JWTAuthentication):
    """
    Extends SimpleJWT to reconstruct CustomerUser objects from tokens
    that carry `is_customer=True`.
    """

    def get_user(self, validated_token):
        is_customer = validated_token.get('is_customer', False)

        if is_customer:
            from apps.contacts.models import Contact
            contact_id = validated_token.get('contact_id')
            try:
                contact = Contact.objects.select_related('organization').get(pk=contact_id)
            except Contact.DoesNotExist:
                raise InvalidToken('Customer contact not found.')
            return CustomerUser(contact)

        return super().get_user(validated_token)
