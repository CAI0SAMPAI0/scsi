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
            user = User.objects.get(email__iexact=login_email)
        except User.DoesNotExist:
            make_password(password)  # timing-safe dummy hash
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
