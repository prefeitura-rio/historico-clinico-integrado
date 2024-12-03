from app.models import User
from app.security import TwoFactorAuth


async def validate_code(user: User, code: str) -> bool:
    if user.is_2fa_required is False:
        return True

    secret_key = await TwoFactorAuth.get_or_create_secret_key(user)
    two_factor_auth = TwoFactorAuth(user, secret_key)

    return two_factor_auth.verify_totp_code(code)
