from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        login_email = email or username
        if not login_email:
            return None
        try:
            user = User.objects.select_related('brokerage').get(email__iexact=login_email)
        except User.DoesNotExist:
            make_password(password)  # timing-safe dummy hash
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.select_related('brokerage').get(pk=user_id)
        except User.DoesNotExist:
            return None

