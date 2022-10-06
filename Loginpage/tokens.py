from django.contrib.auth.tokens import PasswordResetTokenGenerator
import secrets
from six import text_type

class tokengenerate(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return(
            text_type(user.pk) + text_type(timestamp)
        )

generate_token = tokengenerate()