from django.contrib.auth.tokens import PasswordResetTokenGenerator  # for resetting password
from django.utils import six


class TokenGenerator(PasswordResetTokenGenerator):
    # pass
    # only work once not twice
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)


generate_token = TokenGenerator()
